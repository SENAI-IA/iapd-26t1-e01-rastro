from dataclasses import dataclass, field, replace
from typing import Protocol

CAMPOS_COM_ORIGEM = (
    "cve",
    "resumo",
    "cvss",
    "percentil_epss",
    "versoes_afetadas",
    "versao_corrigida",
    "link",
)


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
    origem_dos_campos: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class FonteSemResposta:
    fonte: str
    alvo: str
    motivo: str


class ConsultaNaoRealizada(Exception):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class ConectorDeAvisos(Protocol):
    def consultar(self, pacote: str, versao: str) -> list[Aviso]: ...


def marcar_origem(aviso: Aviso, fonte: str) -> Aviso:
    preenchidos = [campo for campo in CAMPOS_COM_ORIGEM if getattr(aviso, campo) is not None]
    return replace(aviso, origem_dos_campos={campo: fonte for campo in preenchidos})
