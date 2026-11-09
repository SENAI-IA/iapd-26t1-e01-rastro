from dataclasses import dataclass
from typing import Literal

from rastro.identificacao.modelos import Evidencia

SituacaoDaChecagem = Literal["falhou", "passou", "nao_verificada"]
Severidade = Literal["alta", "media", "baixa"]


@dataclass(frozen=True)
class RegraDeChecagem:
    id: str
    titulo: str
    severidade: Severidade
    quem_resolve: str


@dataclass(frozen=True)
class Checagem:
    id: str
    titulo: str
    situacao: SituacaoDaChecagem
    severidade: Severidade
    quem_resolve: str
    evidencia: Evidencia | None
    detalhe: str
