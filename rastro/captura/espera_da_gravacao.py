import contextlib
import threading
from collections.abc import Callable

from rastro.captura.sessao import SessaoDeGravacao

FATIA_DE_ESPERA_EM_SEGUNDOS = 0.25


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

    def ler_linha_e_marcar_que_apertou() -> None:
        with contextlib.suppress(EOFError):
            ler_linha()
        apertou.set()

    threading.Thread(target=ler_linha_e_marcar_que_apertou, daemon=True).start()
    while not apertou.is_set():
        if parada.motivo is not None or not sessao.aberta():
            return False
        sessao.esperar(FATIA_DE_ESPERA_EM_SEGUNDOS)
    return True
