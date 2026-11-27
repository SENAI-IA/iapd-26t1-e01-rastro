import os
import shutil
import sys
import threading
from collections.abc import Callable
from types import TracebackType
from typing import TextIO

from rastro.terminal.cores import ativar_cores_no_terminal
from rastro.terminal.formatacao import cortar_no_limite, destacar

GIRO_EM_BRAILLE = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
MARCA_DE_FEITO = "✓"
GIRO_SEM_UNICODE = "|/-\\"
MARCA_DE_FEITO_SEM_UNICODE = "ok"
INTERVALO_DO_GIRO_EM_SEGUNDOS = 0.1
LARGURA_MINIMA = 20
ESPACO_DO_SIMBOLO_DO_GIRO = 2


def largura_do_terminal() -> int:
    return shutil.get_terminal_size().columns


def console_antigo_do_windows() -> bool:
    return sys.platform == "win32" and "WT_SESSION" not in os.environ


def aceita_os_simbolos(saida: TextIO) -> bool:
    if console_antigo_do_windows():
        return False
    codificacao = getattr(saida, "encoding", None)
    if codificacao is None:
        return True
    try:
        (GIRO_EM_BRAILLE + MARCA_DE_FEITO).encode(codificacao)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def decidir_se_e_ao_vivo(saida: TextIO, ao_vivo: bool | None) -> bool:
    if ao_vivo is not None:
        return ao_vivo
    return saida.isatty()


def decidir_se_usa_cores(ao_vivo: bool, cores: bool | None) -> bool:
    if cores is not None:
        return cores
    if not ao_vivo:
        return False
    return ativar_cores_no_terminal()


class LinhaAoVivo:
    def __init__(
        self,
        saida: TextIO | None = None,
        ao_vivo: bool | None = None,
        largura: Callable[[], int] = largura_do_terminal,
        cores: bool | None = None,
    ) -> None:
        self.saida = saida or sys.stdout
        self.ao_vivo = decidir_se_e_ao_vivo(self.saida, ao_vivo)
        self.cores = decidir_se_usa_cores(self.ao_vivo, cores)
        self.largura = largura
        com_simbolos = aceita_os_simbolos(self.saida)
        self.simbolos_do_giro = GIRO_EM_BRAILLE if com_simbolos else GIRO_SEM_UNICODE
        self.marca_de_feito = MARCA_DE_FEITO if com_simbolos else MARCA_DE_FEITO_SEM_UNICODE
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

    def concluir(self, linha: str) -> None:
        self.imprimir(f"{self.marca_de_feito} {linha}")

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
        simbolo = self.simbolos_do_giro[self._quadro_do_giro % len(self.simbolos_do_giro)]
        linha = f"{simbolo} {cortar_no_limite(self._texto(), largura - ESPACO_DO_SIMBOLO_DO_GIRO)}"
        self.saida.write("\r" + linha.ljust(self._largura_ocupada))
        self.saida.flush()
        self._largura_ocupada = len(linha)

    def _apagar(self) -> None:
        if self._largura_ocupada:
            self.saida.write("\r" + " " * self._largura_ocupada + "\r")
            self.saida.flush()
            self._largura_ocupada = 0
