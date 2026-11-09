from dataclasses import dataclass

from rastro.acao.plano import chave_da_biblioteca
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
from rastro.identificacao.modelos import Biblioteca

AvisosDaBiblioteca = tuple[Biblioteca, list[Aviso]]


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
