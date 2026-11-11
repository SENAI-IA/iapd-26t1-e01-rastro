import os
import shlex
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

MARCA = "Criado por `rastro instalar`. Para remover: rastro desinstalar"
INICIO_DO_BLOCO = "# >>> rastro >>> (criado por `rastro instalar`; `rastro desinstalar` remove)"
FIM_DO_BLOCO = "# <<< rastro <<<"
LINHA_DO_PATH = 'export PATH="$HOME/.local/bin:$PATH"'
ARQUIVOS_DO_SHELL = (".bashrc", ".zshrc", ".profile")
CODIFICACAO_DO_CMD = "oem"
PATH_DO_USUARIO_NO_WINDOWS = "PATH do usuário"
CHAVE_DO_AMBIENTE = "Environment"
TEXTO_PROJETO_NAO_ENCONTRADO = (
    "rode o instalar de dentro da pasta do projeto: python3 -m rastro instalar "
    "(Windows: py -m rastro instalar)"
)
TEXTO_ATALHO_DE_OUTRO = (
    "o comando rastro em {caminho} não foi criado pelo `rastro instalar` "
    "(talvez pelo pipx: remova com `pipx uninstall rastro`). Nada foi alterado."
)


class ProjetoNaoEncontrado(Exception):
    pass


class AtalhoDeOutro(Exception):
    pass


@dataclass(frozen=True)
class Instalacao:
    atalho: Path
    projeto: Path
    path_alterado_em: str | None


@dataclass(frozen=True)
class Desinstalacao:
    atalho_removido: Path | None
    path_removido_de: list[str]


def instalar() -> Instalacao:
    if sys.platform == "win32":
        return instalar_no_windows(Path.home(), os.environ)
    return instalar_no_unix(Path.home(), os.environ)


def desinstalar() -> Desinstalacao:
    if sys.platform == "win32":
        return desinstalar_no_windows(Path.home(), os.environ)
    return desinstalar_no_unix(Path.home())


def instalar_no_unix(casa: Path, ambiente: Mapping[str, str]) -> Instalacao:
    projeto = raiz_do_projeto()
    pasta = casa / ".local" / "bin"
    atalho = pasta / "rastro"
    gravar_atalho(atalho, texto_do_atalho_unix(python_do_sistema(), projeto), "utf-8")
    alterado_em = None
    if not pasta_no_path(pasta, ambiente.get("PATH", "")):
        arquivo = arquivo_do_shell(casa, ambiente.get("SHELL", ""))
        if acrescentar_bloco_do_path(arquivo):
            alterado_em = str(arquivo)
    return Instalacao(atalho, projeto, alterado_em)


def desinstalar_no_unix(casa: Path) -> Desinstalacao:
    removido = remover_atalho(casa / ".local" / "bin" / "rastro")
    arquivos = [casa / nome for nome in ARQUIVOS_DO_SHELL]
    alterados = [str(arquivo) for arquivo in arquivos if remover_bloco_do_path(arquivo)]
    return Desinstalacao(removido, alterados)


def instalar_no_windows(casa: Path, ambiente: Mapping[str, str]) -> Instalacao:
    projeto = raiz_do_projeto()
    pasta = pasta_do_windows(casa, ambiente)
    atalho = pasta / "rastro.cmd"
    texto = texto_do_atalho_windows(python_do_sistema(), projeto)
    gravar_atalho(atalho, texto, CODIFICACAO_DO_CMD)
    alterado = acrescentar_ao_path_do_windows(pasta)
    return Instalacao(atalho, projeto, PATH_DO_USUARIO_NO_WINDOWS if alterado else None)


def desinstalar_no_windows(casa: Path, ambiente: Mapping[str, str]) -> Desinstalacao:
    pasta = pasta_do_windows(casa, ambiente)
    removido = remover_atalho(pasta / "rastro.cmd")
    alterado = remover_do_path_do_windows(pasta)
    return Desinstalacao(removido, [PATH_DO_USUARIO_NO_WINDOWS] if alterado else [])


def raiz_do_projeto() -> Path:
    raiz = Path(__file__).resolve().parent.parent
    if not (raiz / "pyproject.toml").is_file():
        raise ProjetoNaoEncontrado(TEXTO_PROJETO_NAO_ENCONTRADO)
    return raiz


def python_do_sistema() -> Path:
    if sys.prefix == sys.base_prefix:
        return Path(sys.executable)
    python_fora_do_venv = python_da_instalacao(Path(sys.base_prefix))
    return python_fora_do_venv if python_fora_do_venv.is_file() else Path(sys.executable)


def python_da_instalacao(base: Path) -> Path:
    if os.name == "nt":
        return base / "python.exe"
    return base / "bin" / f"python{sys.version_info.major}.{sys.version_info.minor}"


def texto_do_atalho_unix(python: Path, projeto: Path) -> str:
    return (
        "#!/bin/sh\n"
        f"# {MARCA}\n"
        f'PYTHONPATH={shlex.quote(str(projeto))}"${{PYTHONPATH:+:$PYTHONPATH}}" '
        f'exec {shlex.quote(str(python))} -m rastro "$@"\n'
    )


def texto_do_atalho_windows(python: Path, projeto: Path) -> str:
    return (
        "@echo off\r\n"
        f"rem {MARCA}\r\n"
        "setlocal\r\n"
        f'set "PYTHONPATH={projeto};%PYTHONPATH%"\r\n'
        f'"{python}" -m rastro %* & exit /b\r\n'
    )


def gravar_atalho(caminho: Path, texto: str, codificacao: str) -> None:
    if existe(caminho) and not eh_atalho_do_rastro(caminho):
        raise AtalhoDeOutro(TEXTO_ATALHO_DE_OUTRO.format(caminho=caminho))
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding=codificacao, newline="") as arquivo:
        arquivo.write(texto)
    caminho.chmod(0o755)


def remover_atalho(caminho: Path) -> Path | None:
    if not existe(caminho):
        return None
    if not eh_atalho_do_rastro(caminho):
        raise AtalhoDeOutro(TEXTO_ATALHO_DE_OUTRO.format(caminho=caminho))
    caminho.unlink()
    return caminho


def existe(caminho: Path) -> bool:
    return caminho.exists() or caminho.is_symlink()


def eh_atalho_do_rastro(caminho: Path) -> bool:
    if caminho.is_symlink() or not caminho.is_file():
        return False
    try:
        return MARCA in caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def pasta_no_path(pasta: Path, path: str) -> bool:
    return any(Path(parte) == pasta for parte in path.split(os.pathsep) if parte)


def arquivo_do_shell(casa: Path, shell: str) -> Path:
    nome = Path(shell).name
    if nome == "zsh":
        return casa / ".zshrc"
    if nome == "bash":
        return casa / ".bashrc"
    return casa / ".profile"


def acrescentar_bloco_do_path(arquivo: Path) -> bool:
    texto = arquivo.read_text(encoding="utf-8") if arquivo.is_file() else ""
    if INICIO_DO_BLOCO in texto:
        return False
    quebra_que_falta = "" if texto == "" or texto.endswith("\n") else "\n"
    bloco = f"{quebra_que_falta}\n{INICIO_DO_BLOCO}\n{LINHA_DO_PATH}\n{FIM_DO_BLOCO}\n"
    with arquivo.open("a", encoding="utf-8") as saida:
        saida.write(bloco)
    return True


def remover_bloco_do_path(arquivo: Path) -> bool:
    if not arquivo.is_file():
        return False
    linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)
    inicio = posicao_da_linha(linhas, INICIO_DO_BLOCO, 0)
    fim = posicao_da_linha(linhas, FIM_DO_BLOCO, inicio) if inicio is not None else None
    if inicio is None or fim is None:
        return False
    if inicio > 0 and linhas[inicio - 1].strip() == "":
        inicio -= 1
    arquivo.write_text("".join(linhas[:inicio] + linhas[fim + 1 :]), encoding="utf-8")
    return True


def posicao_da_linha(linhas: list[str], procurada: str, a_partir_de: int) -> int | None:
    posicoes = range(a_partir_de, len(linhas))
    return next((i for i in posicoes if linhas[i].strip() == procurada), None)


def pasta_do_windows(casa: Path, ambiente: Mapping[str, str]) -> Path:
    local = ambiente.get("LOCALAPPDATA")
    base = Path(local) if local else casa / "AppData" / "Local"
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

    todas_as_janelas, ambiente_mudou, nao_esperar_travada, espera_em_ms = 0xFFFF, 0x001A, 0x2, 5000
    ctypes.windll.user32.SendMessageTimeoutW(
        todas_as_janelas,
        ambiente_mudou,
        0,
        CHAVE_DO_AMBIENTE,
        nao_esperar_travada,
        espera_em_ms,
        None,
    )
