import shutil
import sys
import threading
from collections.abc import Callable
from types import TracebackType
from typing import TextIO

from rastro.terminal.cores import ativar_cores_no_terminal
from rastro.terminal.formatacao import cortar_no_limite, destacar

SIMBOLOS_DO_GIRO = "|/-\\"
INTERVALO_DO_GIRO_EM_SEGUNDOS = 0.12
LARGURA_MINIMA = 20


def largura_do_terminal() -> int:
    return shutil.get_terminal_size().columns


class LinhaAoVivo:
    def __init__(
        self,
        saida: TextIO | None = None,
        ao_vivo: bool | None = None,
        largura: Callable[[], int] = largura_do_terminal,
        cores: bool | None = None,
    ) -> None:
        self.saida = saida or sys.stdout
        self.ao_vivo = self.saida.isatty() if ao_vivo is None else ao_vivo
        self.cores = (self.ao_vivo and ativar_cores_no_terminal()) if cores is None else cores
        self.largura = largura
        self._texto: Callable[[], str] | None = None
        self._quadro_do_giro = 0
        self._largura_ocupada = 0
        self._trava = threading.Lock()
        self._pedido_de_parada = threading.Event()
        self._tarefa_do_giro: threading.Thread | None = None

    def __enter__(self) -> "LinhaAoVivo":
        if self.ao_vivo:
            self._tarefa_do_giro = threading.Thread(target=self._girar, daemon=True)
            self._tarefa_do_giro.start()
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        erro: BaseException | None,
        rastreio: TracebackType | None,
    ) -> None:
        self._pedido_de_parada.set()
        if self._tarefa_do_giro is not None:
            self._tarefa_do_giro.join()
        self.soltar()

    def acompanhar(self, texto: Callable[[], str]) -> None:
        with self._trava:
            self._texto = texto
            self._desenhar()

    def soltar(self) -> None:
        with self._trava:
            self._apagar()
            self._texto = None

    def imprimir(self, linha: str) -> None:
        with self._trava:
            self._apagar()
            print(linha, file=self.saida, flush=True)
            self._desenhar()

    def pedir(self, linha: str) -> None:
        self.imprimir(destacar(linha) if self.cores else linha)

    def _girar(self) -> None:
        while not self._pedido_de_parada.wait(INTERVALO_DO_GIRO_EM_SEGUNDOS):
            with self._trava:
                self._quadro_do_giro += 1
                self._desenhar()

    def _desenhar(self) -> None:
        if not self.ao_vivo or self._texto is None:
            return
        largura = max(self.largura(), LARGURA_MINIMA) - 1
        simbolo = SIMBOLOS_DO_GIRO[self._quadro_do_giro % len(SIMBOLOS_DO_GIRO)]
        linha = f"{cortar_no_limite(self._texto(), largura - 2)} {simbolo}"
        self.saida.write("\r" + linha.ljust(self._largura_ocupada))
        self.saida.flush()
        self._largura_ocupada = len(linha)

    def _apagar(self) -> None:
        if self._largura_ocupada:
            self.saida.write("\r" + " " * self._largura_ocupada + "\r")
            self.saida.flush()
            self._largura_ocupada = 0
