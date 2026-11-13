from typing import Protocol


class Andamento(Protocol):
    def comecar(self, etapas: int) -> None: ...

    def etapa(self, nome: str) -> None: ...

    def itens(self, total: int) -> None: ...

    def avancar(self) -> None: ...


class SemAndamento:
    def comecar(self, etapas: int) -> None:
        return None

    def etapa(self, nome: str) -> None:
        return None

    def itens(self, total: int) -> None:
        return None

    def avancar(self) -> None:
        return None


SEM_ANDAMENTO = SemAndamento()
