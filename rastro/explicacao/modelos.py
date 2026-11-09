from dataclasses import dataclass


@dataclass(frozen=True)
class Explicacao:
    o_que_e: str
    impacto: str
    como_corrigir: str
    teste_verificacao: str
    gerada_por_ia: bool
