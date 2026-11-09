import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rastro.acao.modelos import Acao
from rastro.acao.plano import chave_da_biblioteca, montar_plano_de_acao
from rastro.configuracao.checagens import checar_configuracao
from rastro.configuracao.modelos import Checagem
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.conector import Aviso, ConectorDeAvisos, ConsultaNaoRealizada
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.har.leitor import ler_har
from rastro.har.site import descobrir_site_analisado
from rastro.identificacao.assinaturas import algum_script_com_conteudo, identificar_por_assinatura
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado
from rastro.risco.nota import calcular_nota
from rastro.risco.prioridade import ordenar_achados
from rastro.travas.conferencia import conferir_bibliotecas
from rastro.travas.faixa_de_versao import descartar_fora_da_faixa
from rastro.travas.modelos import TravaAcionada

AvisosDaBiblioteca = tuple[Biblioteca, list[Aviso]]


@dataclass(frozen=True)
class Analise:
    har: str
    site: str | None
    inicio: datetime
    duracao_s: float
    provedor_de_ia: str | None
    tem_javascript: bool
    bibliotecas: list[Biblioteca]
    a_confirmar: list[Biblioteca]
    nao_consultadas: dict[str, str]
    achados: list[Achado]
    explicacoes: dict[str, Explicacao]
    checagens: list[Checagem]
    plano_de_acao: list[Acao]
    travas_acionadas: list[TravaAcionada]


@dataclass(frozen=True)
class AvisosConsultados:
    avisos: list[AvisosDaBiblioteca]
    nao_consultadas: dict[str, str]


def analisar(
    caminho_har: Path, fonte: ConectorDeAvisos, registro: RegistroDePacotes
) -> Analise:
    inicio = datetime.now()
    cronometro = time.perf_counter()

    requisicoes = ler_har(caminho_har)
    site = descobrir_site_analisado(requisicoes)
    bibliotecas = conferir_bibliotecas(identificar_por_assinatura(requisicoes), registro)
    consultados = consultar_avisos(bibliotecas.confirmadas, fonte)
    avisos_na_faixa, travas_da_faixa = conferir_faixas(consultados.avisos)
    achados = calcular_risco(avisos_na_faixa)
    explicacoes: dict[str, Explicacao] = {}
    checagens = checar_configuracao(requisicoes, site)
    plano = montar_plano_de_acao(achados, explicacoes, checagens)

    return Analise(
        har=caminho_har.name,
        site=site,
        inicio=inicio,
        duracao_s=round(time.perf_counter() - cronometro, 1),
        provedor_de_ia=None,
        tem_javascript=algum_script_com_conteudo(requisicoes),
        bibliotecas=bibliotecas.confirmadas,
        a_confirmar=bibliotecas.a_confirmar,
        nao_consultadas=consultados.nao_consultadas,
        achados=achados,
        explicacoes=explicacoes,
        checagens=checagens,
        plano_de_acao=plano,
        travas_acionadas=bibliotecas.travas_acionadas + travas_da_faixa,
    )


def consultar_avisos(bibliotecas: list[Biblioteca], fonte: ConectorDeAvisos) -> AvisosConsultados:
    avisos: list[AvisosDaBiblioteca] = []
    nao_consultadas: dict[str, str] = {}
    for biblioteca in bibliotecas:
        try:
            avisos.append((biblioteca, fonte.consultar(biblioteca.pacote, biblioteca.versao)))
        except ConsultaNaoRealizada as erro:
            nao_consultadas[chave_da_biblioteca(biblioteca)] = erro.motivo
    return AvisosConsultados(avisos, nao_consultadas)


def conferir_faixas(
    avisos: list[AvisosDaBiblioteca],
) -> tuple[list[AvisosDaBiblioteca], list[TravaAcionada]]:
    mantidos: list[AvisosDaBiblioteca] = []
    travas_acionadas: list[TravaAcionada] = []
    for biblioteca, avisos_da_biblioteca in avisos:
        na_faixa, barrados = descartar_fora_da_faixa(
            biblioteca.pacote, biblioteca.versao, avisos_da_biblioteca
        )
        mantidos.append((biblioteca, na_faixa))
        travas_acionadas.extend(barrados)
    return mantidos, travas_acionadas


def calcular_risco(avisos: list[AvisosDaBiblioteca]) -> list[Achado]:
    achados = []
    for biblioteca, avisos_da_biblioteca in avisos:
        for aviso in avisos_da_biblioteca:
            nota = calcular_nota(aviso.cvss, aviso.percentil_epss)
            achados.append(Achado(biblioteca, aviso, nota))
    return ordenar_achados(achados)
