import os
import shutil
import sys
import threading
import time
from collections.abc import Callable
from types import TracebackType
from typing import TextIO

GIRO = "|/-\\"
INTERVALO_DO_GIRO_EM_SEGUNDOS = 0.12
LARGURA_MINIMA = 20
TEXTO_DA_ETAPA = "[{numero}/{total}] {nome}"
TEXTO_DOS_ITENS = "{feitos} de {total}"
TEXTO_ETAPA_FEITA = "ok"
DESTAQUE = "\x1b[1;33m"
FIM_DO_DESTAQUE = "\x1b[0m"
VARIAVEL_SEM_CORES = "NO_COLOR"
SAIDA_PADRAO_DO_WINDOWS = -11
PROCESSAR_SEQUENCIAS_DO_TERMINAL = 0x0004


def ligar_cores() -> bool:
    if os.environ.get(VARIAVEL_SEM_CORES):
        return False
    if sys.platform != "win32":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        console = kernel32.GetStdHandle(SAIDA_PADRAO_DO_WINDOWS)
        modo = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(console, ctypes.byref(modo)):
            return False
        return bool(kernel32.SetConsoleMode(console, modo.value | PROCESSAR_SEQUENCIAS_DO_TERMINAL))
    except (AttributeError, OSError):
        return False


def destacar(texto: str) -> str:
    return "\n".join(f"{DESTAQUE}{linha}{FIM_DO_DESTAQUE}" for linha in texto.split("\n"))


def largura_do_terminal() -> int:
    return shutil.get_terminal_size().columns


def escrever_tempo(segundos: float) -> str:
    minutos, resto = divmod(int(segundos), 60)
    return f"{minutos}:{resto:02d}"


def cortar(texto: str, largura: int) -> str:
    if len(texto) <= largura:
        return texto
    return texto[: max(largura - 1, 0)] + "…"


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
        self.cores = (self.ao_vivo and ligar_cores()) if cores is None else cores
        self.largura = largura
        self._texto: Callable[[], str] | None = None
        self._giro = 0
        self._ocupada = 0
        self._trava = threading.Lock()
        self._parar = threading.Event()
        self._fio: threading.Thread | None = None

    def __enter__(self) -> "LinhaAoVivo":
        if self.ao_vivo:
            self._fio = threading.Thread(target=self._girar, daemon=True)
            self._fio.start()
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        erro: BaseException | None,
        rastreio: TracebackType | None,
    ) -> None:
        self._parar.set()
        if self._fio is not None:
            self._fio.join()
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
        while not self._parar.wait(INTERVALO_DO_GIRO_EM_SEGUNDOS):
            with self._trava:
                self._giro += 1
                self._desenhar()

    def _desenhar(self) -> None:
        if not self.ao_vivo or self._texto is None:
            return
        largura = max(self.largura(), LARGURA_MINIMA) - 1
        linha = f"{cortar(self._texto(), largura - 2)} {GIRO[self._giro % len(GIRO)]}"
        self.saida.write("\r" + linha.ljust(self._ocupada))
        self.saida.flush()
        self._ocupada = len(linha)

    def _apagar(self) -> None:
        if self._ocupada:
            self.saida.write("\r" + " " * self._ocupada + "\r")
            self.saida.flush()
            self._ocupada = 0


class AndamentoNoTerminal:
    def __init__(self, linha: LinhaAoVivo, relogio: Callable[[], float] = time.monotonic) -> None:
        self.linha = linha
        self.relogio = relogio
        self.total = 0
        self.numero = 0
        self.nome: str | None = None
        self.inicio = 0.0
        self.total_de_itens = 0
        self.feitos = 0

    def comecar(self, etapas: int) -> None:
        self.total = etapas

    def etapa(self, nome: str) -> None:
        self.terminar()
        self.numero += 1
        self.nome = nome
        self.inicio = self.relogio()
        self.total_de_itens = 0
        self.feitos = 0
        if self.linha.ao_vivo:
            self.linha.acompanhar(self.texto)
        else:
            self.linha.imprimir(self.titulo())

    def itens(self, total: int) -> None:
        self.total_de_itens = total

    def avancar(self) -> None:
        self.feitos += 1

    def terminar(self) -> None:
        if self.nome is None:
            return
        if self.linha.ao_vivo:
            self.linha.soltar()
            self.linha.imprimir(f"{self.texto()} · {TEXTO_ETAPA_FEITA}")
        self.nome = None

    def titulo(self) -> str:
        return TEXTO_DA_ETAPA.format(numero=self.numero, total=self.total, nome=self.nome)

    def texto(self) -> str:
        partes = [self.titulo()]
        if self.total_de_itens:
            feitos = min(self.feitos, self.total_de_itens)
            partes.append(TEXTO_DOS_ITENS.format(feitos=feitos, total=self.total_de_itens))
        partes.append(escrever_tempo(self.relogio() - self.inicio))
        return " · ".join(partes)
