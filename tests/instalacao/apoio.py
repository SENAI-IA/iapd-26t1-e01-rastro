import os
from pathlib import Path

import pytest

from rastro.instalacao.sobras import MARCA_DO_INSTALADOR

PATH_SEM_A_PASTA = "/usr/bin:/bin"
somente_unix = pytest.mark.skipif(os.name == "nt", reason="atalho de shell do Linux")


def atalho_unix(pasta_do_usuario: Path) -> Path:
    return pasta_do_usuario / ".local" / "bin" / "rastro"


def ambiente(
    pasta_do_usuario: Path, path: str = PATH_SEM_A_PASTA, shell: str = "/bin/bash"
) -> dict[str, str]:
    return {"PATH": path, "SHELL": shell, "HOME": str(pasta_do_usuario)}


def projeto_do_install_sh(pasta_do_usuario: Path) -> Path:
    projeto = pasta_do_usuario / ".local" / "share" / "rastro"
    projeto.mkdir(parents=True)
    (projeto / MARCA_DO_INSTALADOR).touch()
    return projeto
