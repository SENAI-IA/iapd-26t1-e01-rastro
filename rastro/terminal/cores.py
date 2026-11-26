import os
import sys

VARIAVEL_SEM_CORES = "NO_COLOR"
SAIDA_PADRAO_DO_WINDOWS = -11
PROCESSAR_SEQUENCIAS_DO_TERMINAL = 0x0004


def ativar_cores_no_terminal() -> bool:
    if os.environ.get(VARIAVEL_SEM_CORES):
        return False
    if sys.platform != "win32":
        return True
    return ativar_sequencias_no_console_do_windows()


def ativar_sequencias_no_console_do_windows() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        console = kernel32.GetStdHandle(SAIDA_PADRAO_DO_WINDOWS)
        modo = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(console, ctypes.byref(modo)):
            return False
        novo_modo = modo_com_sequencias_do_terminal(modo.value)
        return bool(kernel32.SetConsoleMode(console, novo_modo))
    except (AttributeError, OSError):
        return False


def modo_com_sequencias_do_terminal(modo_atual: int) -> int:
    return modo_atual | PROCESSAR_SEQUENCIAS_DO_TERMINAL
