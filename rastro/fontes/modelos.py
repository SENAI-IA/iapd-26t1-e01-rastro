from dataclasses import dataclass, field, replace

from rastro.identificacao.modelos import Biblioteca

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


@dataclass(frozen=True)
class AvisosDaBiblioteca:
    biblioteca: Biblioteca
    avisos: list[Aviso]


def marcar_origem(aviso: Aviso, fonte: str) -> Aviso:
    origem_dos_campos = {}
    for campo in campos_preenchidos(aviso):
        origem_dos_campos[campo] = fonte
    return replace(aviso, origem_dos_campos=origem_dos_campos)


def campos_preenchidos(aviso: Aviso) -> list[str]:
    preenchidos = []
    for campo in CAMPOS_COM_ORIGEM:
        if getattr(aviso, campo) is not None:
            preenchidos.append(campo)
    return preenchidos
