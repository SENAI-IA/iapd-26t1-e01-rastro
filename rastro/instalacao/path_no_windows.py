import sys
from collections.abc import Callable, Mapping
from pathlib import Path

CHAVE_DO_AMBIENTE = "Environment"
TODAS_AS_JANELAS = 0xFFFF
AVISO_DE_AMBIENTE_MUDOU = 0x001A
NAO_ESPERAR_JANELA_TRAVADA = 0x2
ESPERA_DO_AVISO_EM_MILISSEGUNDOS = 5000


def pasta_do_windows(pasta_do_usuario: Path, ambiente: Mapping[str, str]) -> Path:
    local = ambiente.get("LOCALAPPDATA")
    base = Path(local) if local else pasta_do_usuario / "AppData" / "Local"
    return base / "Rastro" / "bin"


def acrescentar_ao_path_do_windows(pasta: Path) -> bool:
    return trocar_path_do_windows(lambda partes: acrescentar_pasta(partes, pasta))


def remover_do_path_do_windows(pasta: Path) -> bool:
    return trocar_path_do_windows(lambda partes: tirar_pasta(partes, pasta))


def acrescentar_pasta(partes: list[str], pasta: Path) -> list[str]:
    if any(mesma_pasta_no_windows(parte, pasta) for parte in partes):
        return partes
    return [*partes, str(pasta)]


def tirar_pasta(partes: list[str], pasta: Path) -> list[str]:
    return [parte for parte in partes if not mesma_pasta_no_windows(parte, pasta)]


def mesma_pasta_no_windows(parte: str, pasta: Path) -> bool:
    return parte.lower() == str(pasta).lower()


def trocar_path_do_windows(trocar: Callable[[list[str]], list[str]]) -> bool:
    if sys.platform != "win32":
        raise OSError("o PATH do usuário no registro só existe no Windows")
    import winreg

    acesso = winreg.KEY_READ | winreg.KEY_WRITE
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CHAVE_DO_AMBIENTE, 0, acesso) as chave:
        try:
            valor, tipo = winreg.QueryValueEx(chave, "Path")
        except FileNotFoundError:
            valor, tipo = "", winreg.REG_EXPAND_SZ
        partes = [parte for parte in str(valor).split(";") if parte]
        novas = trocar(partes)
        if novas == partes:
            return False
        winreg.SetValueEx(chave, "Path", 0, tipo, ";".join(novas))
    avisar_terminais_novos_do_windows()
    return True


def avisar_terminais_novos_do_windows() -> None:
    if sys.platform != "win32":
        return
    import ctypes

    ctypes.windll.user32.SendMessageTimeoutW(
        TODAS_AS_JANELAS,
        AVISO_DE_AMBIENTE_MUDOU,
        0,
        CHAVE_DO_AMBIENTE,
        NAO_ESPERAR_JANELA_TRAVADA,
        ESPERA_DO_AVISO_EM_MILISSEGUNDOS,
        None,
    )
