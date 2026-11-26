from typing import Protocol


class FalhaAoNavegar(Exception):
    pass


class SessaoDeGravacao(Protocol):
    requisicoes: int
    scripts: int

    def abrir_pagina(self, url: str) -> None: ...

    def links(self) -> list[str]: ...

    def endereco(self) -> str: ...

    def aberta(self) -> bool: ...

    def esperar(self, segundos: float) -> None: ...
