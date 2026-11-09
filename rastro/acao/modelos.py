from dataclasses import dataclass

from rastro.risco.modelos import Prioridade


@dataclass(frozen=True)
class Acao:
    id: str
    prioridade: Prioridade
    nota: float | None
    o_que_fazer: str
    porque: str
    impacto: str
    quem_resolve: str
    refs: list[str]
    teste_verificacao: str | None
    texto_task: str = ""


@dataclass(frozen=True)
class CorrecaoDaChecagem:
    o_que_fazer: str
    impacto: str
