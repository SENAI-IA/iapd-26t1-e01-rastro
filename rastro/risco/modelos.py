from dataclasses import dataclass
from typing import Literal

from rastro.fontes.conector import Aviso
from rastro.identificacao.modelos import Biblioteca

Prioridade = Literal["alta", "media", "baixa", "a avaliar"]


@dataclass(frozen=True)
class Nota:
    valor: float | None
    prioridade: Prioridade
    conta: str
    sem_epss: bool


@dataclass(frozen=True)
class Achado:
    biblioteca: Biblioteca
    aviso: Aviso
    nota: Nota
