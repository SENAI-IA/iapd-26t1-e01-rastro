import contextlib
import threading
from collections.abc import Callable
from typing import Protocol

FATIA_DE_ESPERA_EM_SEGUNDOS = 0.25


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


class PedidoDeParada:
    def __init__(self) -> None:
        self.motivo: str | None = None

    def pedir(self, motivo: str) -> None:
        if self.motivo is None:
            self.motivo = motivo


def esperar_a_janela_fechar(sessao: SessaoDeGravacao, parada: PedidoDeParada) -> None:
    while sessao.aberta() and parada.motivo is None:
        sessao.esperar(FATIA_DE_ESPERA_EM_SEGUNDOS)


def esperar_o_enter(
    sessao: SessaoDeGravacao, parada: PedidoDeParada, ler_linha: Callable[[], str] = input
) -> bool:
    apertou = threading.Event()

    def ler() -> None:
        with contextlib.suppress(EOFError):
            ler_linha()
        apertou.set()

    threading.Thread(target=ler, daemon=True).start()
    while not apertou.is_set():
        if parada.motivo is not None or not sessao.aberta():
            return False
        sessao.esperar(FATIA_DE_ESPERA_EM_SEGUNDOS)
    return True
