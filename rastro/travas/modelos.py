from dataclasses import dataclass


@dataclass(frozen=True)
class TravaAcionada:
    trava: str
    alvo: str
    motivo: str
