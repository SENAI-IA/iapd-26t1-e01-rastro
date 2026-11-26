from datetime import datetime
from pathlib import Path

from rastro.gravacao_segura import caminho_da_pasta_com_data

NOME_DO_HAR = "visita.har"
PERMISSAO_SO_DO_DONO = 0o700


class GravacaoJaExiste(Exception):
    def __init__(self, pasta: Path) -> None:
        super().__init__(
            f"a pasta da gravação já existe: {pasta}. "
            "Nada foi gravado: o Rastro nunca sobrescreve uma gravação."
        )


def pasta_padrao_das_gravacoes() -> Path:
    return Path.home() / "Rastro" / "gravacoes"


def caminho_da_gravacao(pasta_das_gravacoes: Path, host: str, momento: datetime) -> Path:
    return caminho_da_pasta_com_data(pasta_das_gravacoes, host, momento)


def criar_pasta_da_gravacao(pasta: Path) -> Path:
    pasta.parent.mkdir(parents=True, exist_ok=True)
    try:
        pasta.mkdir(mode=PERMISSAO_SO_DO_DONO)
    except FileExistsError as erro:
        raise GravacaoJaExiste(pasta) from erro
    return pasta / NOME_DO_HAR


def apagar_pasta_da_gravacao(pasta: Path) -> None:
    (pasta / NOME_DO_HAR).unlink(missing_ok=True)
    pasta.rmdir()
