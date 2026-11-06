from dataclasses import dataclass
from typing import Literal

MetodoDeIdentificacao = Literal["assinatura", "ia"]
SituacaoDaBiblioteca = Literal["confirmada", "a_confirmar"]


@dataclass(frozen=True)
class Evidencia:
    indice_requisicao: int
    url: str
    trecho: str | None


@dataclass(frozen=True)
class Biblioteca:
    pacote: str
    versao: str
    metodo: MetodoDeIdentificacao
    situacao: SituacaoDaBiblioteca
    conferida_no_npm: bool | None
    travas_que_falharam: list[str]
    evidencias: list[Evidencia]
