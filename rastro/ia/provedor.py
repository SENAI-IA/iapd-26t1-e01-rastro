from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RespostaDoProvedor:
    texto: str
    tokens: int | None


class FalhaDoProvedor(Exception):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class ProvedorDeIA(Protocol):
    nome: str

    def executar(self, prompt: str) -> RespostaDoProvedor: ...
