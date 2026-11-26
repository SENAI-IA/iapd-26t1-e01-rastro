import shlex
from dataclasses import dataclass
from pathlib import Path

from rastro.instalacao.atalho import pasta_do_projeto

MARCA_DO_INSTALADOR = ".instalado-pelo-install-sh"
PASTA_DOS_DADOS = "Rastro"
DESCRICAO_DOS_ARQUIVOS = "os arquivos do Rastro"
DESCRICAO_DOS_DADOS = "suas gravações e relatórios (guarde antes o que quiser manter)"


@dataclass(frozen=True)
class Sobra:
    descricao: str
    caminho: Path


def sobras() -> list[Sobra]:
    return sobras_da_instalacao(Path.home(), pasta_do_projeto())


def sobras_da_instalacao(pasta_do_usuario: Path, projeto: Path) -> list[Sobra]:
    encontradas = []
    if instalado_pelo_install_sh(projeto):
        encontradas.append(Sobra(DESCRICAO_DOS_ARQUIVOS, projeto))
    dados = pasta_do_usuario / PASTA_DOS_DADOS
    if dados.is_dir():
        encontradas.append(Sobra(DESCRICAO_DOS_DADOS, dados))
    return encontradas


def instalado_pelo_install_sh(projeto: Path) -> bool:
    return (projeto / MARCA_DO_INSTALADOR).is_file()


def comando_para_apagar(caminho: Path, no_windows: bool) -> str:
    if no_windows:
        entre_aspas = str(caminho).replace("'", "''")
        return f"Remove-Item -Recurse -Force '{entre_aspas}'"
    return f"rm -rf {shlex.quote(str(caminho))}"
