import re
from datetime import datetime
from pathlib import Path

FORMATO_DA_PASTA_COM_DATA = "%Y-%m-%d_%H-%M-%S"
CARACTERES_PROIBIDOS_NO_WINDOWS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
NOMES_RESERVADOS_NO_WINDOWS = frozenset(
    ["CON", "PRN", "AUX", "NUL"]
    + [f"COM{numero}" for numero in range(1, 10)]
    + [f"LPT{numero}" for numero in range(1, 10)]
)


class PastaJaExiste(Exception):
    def __init__(self, pasta: Path) -> None:
        super().__init__(f"a pasta já existe: {pasta}")


def nome_de_pasta_seguro(nome: str) -> str:
    seguro = CARACTERES_PROIBIDOS_NO_WINDOWS.sub("_", nome).rstrip(". ")
    if not seguro:
        return "_"
    if nome_e_reservado_no_windows(seguro):
        return f"_{seguro}"
    return seguro


def nome_e_reservado_no_windows(nome: str) -> bool:
    return nome.split(".")[0].upper() in NOMES_RESERVADOS_NO_WINDOWS


def caminho_da_pasta_com_data(pasta_de_destino: Path, nome: str, momento: datetime) -> Path:
    return (
        pasta_de_destino / nome_de_pasta_seguro(nome) / momento.strftime(FORMATO_DA_PASTA_COM_DATA)
    )


def criar_pasta_nova(pasta: Path) -> None:
    pasta.parent.mkdir(parents=True, exist_ok=True)
    try:
        pasta.mkdir()
    except FileExistsError as erro:
        raise PastaJaExiste(pasta) from erro


def gravar_arquivo_novo(caminho: Path, texto: str) -> None:
    with open(caminho, "x", encoding="utf-8") as arquivo:
        arquivo.write(texto)
