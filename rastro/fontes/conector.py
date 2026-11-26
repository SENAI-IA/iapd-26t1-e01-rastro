from typing import Protocol

from rastro.fontes.modelos import Aviso


class ConsultaNaoRealizada(Exception):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class ConectorDeAvisos(Protocol):
    def consultar(self, pacote: str, versao: str) -> list[Aviso]: ...
