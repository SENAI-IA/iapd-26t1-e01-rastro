import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from rastro.instalacao.atalho import (
    gravar_atalho,
    python_do_sistema,
    raiz_do_projeto,
    remover_atalho,
    texto_do_atalho_unix,
    texto_do_atalho_windows,
)
from rastro.instalacao.path_no_unix import (
    ARQUIVOS_DO_SHELL,
    acrescentar_bloco_do_path,
    arquivo_do_shell,
    pasta_no_path,
    remover_bloco_do_path,
)
from rastro.instalacao.path_no_windows import (
    acrescentar_ao_path_do_windows,
    pasta_do_windows,
    remover_do_path_do_windows,
)

CODIFICACAO_DO_CMD = "oem"
PATH_DO_USUARIO_NO_WINDOWS = "PATH do usuário"


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


def instalar_no_unix(pasta_do_usuario: Path, ambiente: Mapping[str, str]) -> Instalacao:
    projeto = raiz_do_projeto()
    pasta = pasta_do_usuario / ".local" / "bin"
    atalho = pasta / "rastro"
    gravar_atalho(atalho, texto_do_atalho_unix(python_do_sistema(), projeto), "utf-8")
    arquivo_alterado = None
    if not pasta_no_path(pasta, ambiente.get("PATH", "")):
        arquivo = arquivo_do_shell(pasta_do_usuario, ambiente.get("SHELL", ""))
        if acrescentar_bloco_do_path(arquivo):
            arquivo_alterado = str(arquivo)
    return Instalacao(atalho, projeto, arquivo_alterado)


def desinstalar_no_unix(pasta_do_usuario: Path) -> Desinstalacao:
    removido = remover_atalho(pasta_do_usuario / ".local" / "bin" / "rastro")
    arquivos = [pasta_do_usuario / nome for nome in ARQUIVOS_DO_SHELL]
    arquivos_alterados = [str(arquivo) for arquivo in arquivos if remover_bloco_do_path(arquivo)]
    return Desinstalacao(removido, arquivos_alterados)


def instalar_no_windows(pasta_do_usuario: Path, ambiente: Mapping[str, str]) -> Instalacao:
    projeto = raiz_do_projeto()
    pasta = pasta_do_windows(pasta_do_usuario, ambiente)
    atalho = pasta / "rastro.cmd"
    texto = texto_do_atalho_windows(python_do_sistema(), projeto)
    gravar_atalho(atalho, texto, CODIFICACAO_DO_CMD)
    path_foi_alterado = acrescentar_ao_path_do_windows(pasta)
    return Instalacao(atalho, projeto, PATH_DO_USUARIO_NO_WINDOWS if path_foi_alterado else None)


def desinstalar_no_windows(pasta_do_usuario: Path, ambiente: Mapping[str, str]) -> Desinstalacao:
    pasta = pasta_do_windows(pasta_do_usuario, ambiente)
    removido = remover_atalho(pasta / "rastro.cmd")
    path_foi_alterado = remover_do_path_do_windows(pasta)
    return Desinstalacao(removido, [PATH_DO_USUARIO_NO_WINDOWS] if path_foi_alterado else [])
