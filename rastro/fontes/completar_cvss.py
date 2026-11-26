from dataclasses import dataclass, replace
from typing import Protocol

from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.modelos import Aviso
from rastro.fontes.nvd import NOME_DA_FONTE


class BuscaDeCvss(Protocol):
    def buscar_cvss(self, cve: str) -> float | None: ...


@dataclass(frozen=True)
class CvssCompletado:
    avisos: list[Aviso]
    nao_responderam: dict[str, str]


def completar_cvss(avisos: list[Aviso], busca_de_cvss: BuscaDeCvss) -> CvssCompletado:
    cvss_por_cve: dict[str, float | None] = {}
    nao_responderam: dict[str, str] = {}
    for cve in cves_sem_cvss(avisos):
        try:
            cvss_por_cve[cve] = busca_de_cvss.buscar_cvss(cve)
        except ConsultaNaoRealizada as erro:
            nao_responderam[cve] = erro.motivo
    completados = [aplicar_cvss(aviso, cvss_por_cve) for aviso in avisos]
    return CvssCompletado(completados, nao_responderam)


def cves_sem_cvss(avisos: list[Aviso]) -> list[str]:
    cves = [aviso.cve for aviso in avisos if aviso.cve is not None and aviso.cvss is None]
    return list(dict.fromkeys(cves))


def aplicar_cvss(aviso: Aviso, cvss_por_cve: dict[str, float | None]) -> Aviso:
    if aviso.cve is None or aviso.cvss is not None:
        return aviso
    cvss = cvss_por_cve.get(aviso.cve)
    if cvss is None:
        return aviso
    return replace(
        aviso,
        cvss=cvss,
        fontes=[*aviso.fontes, NOME_DA_FONTE],
        origem_dos_campos={**aviso.origem_dos_campos, "cvss": NOME_DA_FONTE},
    )
