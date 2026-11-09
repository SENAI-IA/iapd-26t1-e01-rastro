from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Aviso:
    fontes: list[str]
    apelidos: list[str]
    ghsa: str
    cve: str | None
    resumo: str
    cvss: float | None
    percentil_epss: float | None
    versoes_afetadas: str
    versao_corrigida: str | None
    link: str


class ConsultaNaoRealizada(Exception):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class ConectorDeAvisos(Protocol):
    def consultar(self, pacote: str, versao: str) -> list[Aviso]: ...
