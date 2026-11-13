import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rastro.acao.modelos import Acao
from rastro.acao.plano import montar_plano_de_acao
from rastro.configuracao.checagens import checar_configuracao
from rastro.configuracao.modelos import Checagem
from rastro.explicacao.ia import explicar_achados
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.conector import ConectorDeAvisos, FonteSemResposta
from rastro.fontes.consulta import AvisosDaBiblioteca, consultar_avisos
from rastro.fontes.nvd import BuscaDeCvss
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.har.leitor import ler_har
from rastro.har.site import descobrir_site_analisado
from rastro.har.visita import PassoDaVisita, montar_visita
from rastro.ia.cliente import ChamadaIA, ClienteDeIA
from rastro.identificacao.assinaturas import algum_script_com_conteudo, identificar_por_assinatura
from rastro.identificacao.ia import identificar_em_bundles
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.achados import calcular_risco
from rastro.risco.modelos import Achado
from rastro.travas.conferencia import conferir_bibliotecas
from rastro.travas.faixa_de_versao import descartar_fora_da_faixa
from rastro.travas.modelos import TravaAcionada


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
    visita: list[PassoDaVisita]


def analisar(
    caminho_har: Path,
    fonte: ConectorDeAvisos,
    registro: RegistroDePacotes,
    ia: ClienteDeIA | None = None,
    osv: ConectorDeAvisos | None = None,
    nvd: BuscaDeCvss | None = None,
    gravado_pelo_rastro: bool = False,
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
    checagens = checar_configuracao(requisicoes, site, gravado_pelo_rastro)
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
        visita=montar_visita(requisicoes),
    )


def nome_do_provedor(ia: ClienteDeIA | None) -> str | None:
    if ia is None:
        return None
    return ia.provedor.nome


def chamadas_feitas(ia: ClienteDeIA | None) -> list[ChamadaIA]:
    if ia is None:
        return []
    return list(ia.chamadas)


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
