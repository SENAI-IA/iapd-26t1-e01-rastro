from dataclasses import dataclass

from rastro.andamento import ANDAMENTO_SILENCIOSO, Andamento
from rastro.fontes import nvd, osv
from rastro.fontes.completar_cvss import BuscaDeCvss, completar_cvss
from rastro.fontes.conector import ConectorDeAvisos, ConsultaNaoRealizada
from rastro.fontes.juncao_dos_avisos import juntar_avisos
from rastro.fontes.modelos import Aviso, AvisosDaBiblioteca, FonteSemResposta
from rastro.identificacao.modelos import Biblioteca, nome_com_versao


@dataclass(frozen=True)
class AvisosConsultados:
    avisos: list[AvisosDaBiblioteca]
    nao_consultadas: dict[str, str]
    fontes_sem_resposta: list[FonteSemResposta]


@dataclass(frozen=True)
class AvisosDeUmaFonte:
    avisos: list[Aviso]
    sem_resposta: list[FonteSemResposta]


def consultar_avisos(
    bibliotecas: list[Biblioteca],
    fonte: ConectorDeAvisos,
    conector_osv: ConectorDeAvisos | None = None,
    busca_de_cvss: BuscaDeCvss | None = None,
    andamento: Andamento = ANDAMENTO_SILENCIOSO,
) -> AvisosConsultados:
    avisos: list[AvisosDaBiblioteca] = []
    nao_consultadas: dict[str, str] = {}
    fontes_sem_resposta: list[FonteSemResposta] = []
    andamento.definir_total_de_itens(len(bibliotecas))
    for biblioteca in bibliotecas:
        try:
            consultada = consultar_uma_biblioteca(biblioteca, fonte, conector_osv, busca_de_cvss)
        except ConsultaNaoRealizada as erro:
            nao_consultadas[nome_com_versao(biblioteca)] = erro.motivo
            andamento.avancar_item()
            continue
        avisos.append(AvisosDaBiblioteca(biblioteca, consultada.avisos))
        fontes_sem_resposta.extend(consultada.sem_resposta)
        andamento.avancar_item()
    return AvisosConsultados(avisos, nao_consultadas, fontes_sem_resposta)


def consultar_uma_biblioteca(
    biblioteca: Biblioteca,
    fonte: ConectorDeAvisos,
    conector_osv: ConectorDeAvisos | None,
    busca_de_cvss: BuscaDeCvss | None,
) -> AvisosDeUmaFonte:
    do_github = fonte.consultar(biblioteca.pacote, biblioteca.versao)
    do_osv = consultar_osv(biblioteca, conector_osv)
    com_cvss = completar_cvss_pelo_nvd(juntar_avisos(do_github + do_osv.avisos), busca_de_cvss)
    return AvisosDeUmaFonte(com_cvss.avisos, do_osv.sem_resposta + com_cvss.sem_resposta)


def consultar_osv(
    biblioteca: Biblioteca, conector_osv: ConectorDeAvisos | None
) -> AvisosDeUmaFonte:
    if conector_osv is None:
        return AvisosDeUmaFonte([], [])
    try:
        return AvisosDeUmaFonte(conector_osv.consultar(biblioteca.pacote, biblioteca.versao), [])
    except ConsultaNaoRealizada as erro:
        alvo = nome_com_versao(biblioteca)
        return AvisosDeUmaFonte([], [FonteSemResposta(osv.NOME_DA_FONTE, alvo, erro.motivo)])


def completar_cvss_pelo_nvd(
    avisos: list[Aviso], busca_de_cvss: BuscaDeCvss | None
) -> AvisosDeUmaFonte:
    if busca_de_cvss is None:
        return AvisosDeUmaFonte(avisos, [])
    completado = completar_cvss(avisos, busca_de_cvss)
    sem_resposta = [
        FonteSemResposta(nvd.NOME_DA_FONTE, cve, motivo)
        for cve, motivo in completado.nao_responderam.items()
    ]
    return AvisosDeUmaFonte(completado.avisos, sem_resposta)
