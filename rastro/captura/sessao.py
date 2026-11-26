from typing import Protocol


class FalhaAoNavegar(Exception):
    pass


class SessaoDeGravacao(Protocol):
    requisicoes: int
    scripts: int

    def ir(self, url: str) -> None: ...

    def links(self) -> list[str]: ...

    def endereco(self) -> str: ...

    def aberta(self) -> bool: ...

    def esperar(self, segundos: float) -> None: ...
