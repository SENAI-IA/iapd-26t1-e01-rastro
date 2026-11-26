import os
import shlex
import sys
from pathlib import Path

PERMISSAO_DE_LER_E_EXECUTAR = 0o755
MARCA_DO_ATALHO = "Criado por `rastro instalar`. Para remover: rastro desinstalar"
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


def pasta_do_projeto() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def raiz_do_projeto() -> Path:
    pasta = pasta_do_projeto()
    if not (pasta / "pyproject.toml").is_file():
        raise ProjetoNaoEncontrado(TEXTO_PROJETO_NAO_ENCONTRADO)
    return pasta


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
        f"# {MARCA_DO_ATALHO}\n"
        f'PYTHONPATH={shlex.quote(str(projeto))}"${{PYTHONPATH:+:$PYTHONPATH}}" '
        f'exec {shlex.quote(str(python))} -m rastro "$@"\n'
    )


def texto_do_atalho_windows(python: Path, projeto: Path) -> str:
    return (
        "@echo off\r\n"
        f"rem {MARCA_DO_ATALHO}\r\n"
        "setlocal\r\n"
        f'set "PYTHONPATH={projeto};%PYTHONPATH%"\r\n'
        f'"{python}" -m rastro %* & exit /b\r\n'
    )


def gravar_atalho(caminho: Path, texto: str, codificacao: str) -> None:
    if existe(caminho) and not atalho_foi_criado_pelo_rastro(caminho):
        raise AtalhoDeOutro(TEXTO_ATALHO_DE_OUTRO.format(caminho=caminho))
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding=codificacao, newline="") as arquivo:
        arquivo.write(texto)
    caminho.chmod(PERMISSAO_DE_LER_E_EXECUTAR)


def remover_atalho(caminho: Path) -> Path | None:
    if not existe(caminho):
        return None
    if not atalho_foi_criado_pelo_rastro(caminho):
        raise AtalhoDeOutro(TEXTO_ATALHO_DE_OUTRO.format(caminho=caminho))
    caminho.unlink()
    return caminho


def existe(caminho: Path) -> bool:
    return caminho.exists() or caminho.is_symlink()


def atalho_foi_criado_pelo_rastro(caminho: Path) -> bool:
    if caminho.is_symlink() or not caminho.is_file():
        return False
    try:
        return MARCA_DO_ATALHO in caminho.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
