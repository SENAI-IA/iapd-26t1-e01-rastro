import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rastro.acao.modelos import Acao
from rastro.acao.plano import chave_da_biblioteca, montar_plano_de_acao
from rastro.configuracao.checagens import checar_configuracao
from rastro.configuracao.modelos import Checagem
from rastro.explicacao.ia import explicar_achados
from rastro.explicacao.modelos import Explicacao
from rastro.fontes import nvd as fonte_nvd
from rastro.fontes import osv as fonte_osv
from rastro.fontes.conector import (
    Aviso,
    ConectorDeAvisos,
    ConsultaNaoRealizada,
    FonteSemResposta,
)
from rastro.fontes.juncao import juntar_avisos
from rastro.fontes.nvd import BuscaDeCvss, completar_cvss
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.har.leitor import ler_har
from rastro.har.site import descobrir_site_analisado
from rastro.ia.cliente import ChamadaIA, ClienteDeIA
from rastro.identificacao.assinaturas import algum_script_com_conteudo, identificar_por_assinatura
from rastro.identificacao.ia import identificar_em_bundles
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
    fontes_sem_resposta: list[FonteSemResposta]
    achados: list[Achado]
    explicacoes: dict[str, Explicacao]
    checagens: list[Checagem]
    plano_de_acao: list[Acao]
    travas_acionadas: list[TravaAcionada]
    chamadas_de_ia: list[ChamadaIA]


@dataclass(frozen=True)
class AvisosConsultados:
    avisos: list[AvisosDaBiblioteca]
    nao_consultadas: dict[str, str]
    fontes_sem_resposta: list[FonteSemResposta]


@dataclass(frozen=True)
class AvisosDeUmaFonte:
    avisos: list[Aviso]
    sem_resposta: list[FonteSemResposta]


def analisar(
    caminho_har: Path,
    fonte: ConectorDeAvisos,
    registro: RegistroDePacotes,
    ia: ClienteDeIA | None = None,
    osv: ConectorDeAvisos | None = None,
    nvd: BuscaDeCvss | None = None,
) -> Analise:
    inicio = datetime.now()
    cronometro = time.perf_counter()

    requisicoes = ler_har(caminho_har)
    site = descobrir_site_analisado(requisicoes)
    por_assinatura = identificar_por_assinatura(requisicoes)
    em_bundles = identificar_em_bundles(requisicoes, por_assinatura, ia)
    bibliotecas = conferir_bibliotecas(por_assinatura + em_bundles.bibliotecas, registro)
    consultados = consultar_avisos(bibliotecas.confirmadas, fonte, osv, nvd)
    avisos_na_faixa, travas_da_faixa = conferir_faixas(consultados.avisos)
    achados = calcular_risco(avisos_na_faixa)
    explicados = explicar_achados(achados, ia)
    checagens = checar_configuracao(requisicoes, site)
    plano = montar_plano_de_acao(achados, explicados.explicacoes, checagens)

    return Analise(
        har=caminho_har.name,
        site=site,
        inicio=inicio,
        duracao_s=round(time.perf_counter() - cronometro, 1),
        provedor_de_ia=nome_do_provedor(ia),
        tem_javascript=algum_script_com_conteudo(requisicoes),
        bibliotecas=bibliotecas.confirmadas,
        a_confirmar=bibliotecas.a_confirmar,
        nao_consultadas=consultados.nao_consultadas,
        fontes_sem_resposta=consultados.fontes_sem_resposta,
        achados=achados,
        explicacoes=explicados.explicacoes,
        checagens=checagens,
        plano_de_acao=plano,
        travas_acionadas=(
            em_bundles.travas_acionadas
            + bibliotecas.travas_acionadas
            + travas_da_faixa
            + explicados.travas_acionadas
        ),
        chamadas_de_ia=chamadas_feitas(ia),
    )


def nome_do_provedor(ia: ClienteDeIA | None) -> str | None:
    if ia is None:
        return None
    return ia.provedor.nome


def chamadas_feitas(ia: ClienteDeIA | None) -> list[ChamadaIA]:
    if ia is None:
        return []
    return list(ia.chamadas)


def consultar_avisos(
    bibliotecas: list[Biblioteca],
    fonte: ConectorDeAvisos,
    osv: ConectorDeAvisos | None = None,
    nvd: BuscaDeCvss | None = None,
) -> AvisosConsultados:
    avisos: list[AvisosDaBiblioteca] = []
    nao_consultadas: dict[str, str] = {}
    fontes_sem_resposta: list[FonteSemResposta] = []
    for biblioteca in bibliotecas:
        try:
            do_github = fonte.consultar(biblioteca.pacote, biblioteca.versao)
        except ConsultaNaoRealizada as erro:
            nao_consultadas[chave_da_biblioteca(biblioteca)] = erro.motivo
            continue
        do_osv = consultar_osv(biblioteca, osv)
        com_cvss = completar_cvss_pelo_nvd(juntar_avisos(do_github + do_osv.avisos), nvd)
        avisos.append((biblioteca, com_cvss.avisos))
        fontes_sem_resposta.extend(do_osv.sem_resposta + com_cvss.sem_resposta)
    return AvisosConsultados(avisos, nao_consultadas, fontes_sem_resposta)


def consultar_osv(biblioteca: Biblioteca, osv: ConectorDeAvisos | None) -> AvisosDeUmaFonte:
    if osv is None:
        return AvisosDeUmaFonte([], [])
    try:
        return AvisosDeUmaFonte(osv.consultar(biblioteca.pacote, biblioteca.versao), [])
    except ConsultaNaoRealizada as erro:
        alvo = chave_da_biblioteca(biblioteca)
        return AvisosDeUmaFonte([], [FonteSemResposta(fonte_osv.NOME_DA_FONTE, alvo, erro.motivo)])


def completar_cvss_pelo_nvd(avisos: list[Aviso], nvd: BuscaDeCvss | None) -> AvisosDeUmaFonte:
    if nvd is None:
        return AvisosDeUmaFonte(avisos, [])
    completado = completar_cvss(avisos, nvd)
    sem_resposta = [
        FonteSemResposta(fonte_nvd.NOME_DA_FONTE, cve, motivo)
        for cve, motivo in completado.nao_responderam.items()
    ]
    return AvisosDeUmaFonte(completado.avisos, sem_resposta)


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
