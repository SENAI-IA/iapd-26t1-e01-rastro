import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

NOME_DO_JSON = "relatorio.json"
FORMATO_DA_PASTA_DA_ANALISE = "%Y-%m-%d_%H-%M-%S"
CARACTERES_PROIBIDOS_NO_WINDOWS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
NOMES_RESERVADOS_NO_WINDOWS = frozenset(
    ["CON", "PRN", "AUX", "NUL"]
    + [f"COM{numero}" for numero in range(1, 10)]
    + [f"LPT{numero}" for numero in range(1, 10)]
)


class RelatorioJaExiste(Exception):
    def __init__(self, pasta: Path) -> None:
        super().__init__(
            f"a pasta da análise já existe: {pasta}. "
            "Nada foi gravado: o Rastro nunca sobrescreve um relatório."
        )


def pasta_padrao() -> Path:
    return Path.home() / "Rastro" / "relatorios"


def nome_da_aplicacao(site: str | None, caminho_har: Path) -> str:
    if site:
        return site
    return caminho_har.stem


def nome_de_pasta_seguro(nome: str) -> str:
    seguro = CARACTERES_PROIBIDOS_NO_WINDOWS.sub("_", nome).rstrip(". ")
    if not seguro:
        return "_"
    if e_nome_reservado_no_windows(seguro):
        return f"_{seguro}"
    return seguro


def e_nome_reservado_no_windows(nome: str) -> bool:
    return nome.split(".")[0].upper() in NOMES_RESERVADOS_NO_WINDOWS


def caminho_do_relatorio(raiz: Path, aplicacao: str, momento: datetime) -> Path:
    return raiz / nome_de_pasta_seguro(aplicacao) / momento.strftime(FORMATO_DA_PASTA_DA_ANALISE)


def gravar_relatorio(pasta_da_analise: Path, relatorio: dict[str, Any]) -> Path:
    criar_pasta_nova(pasta_da_analise)
    caminho_do_json = pasta_da_analise / NOME_DO_JSON
    with open(caminho_do_json, "x", encoding="utf-8") as arquivo:
        json.dump(relatorio, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
    return caminho_do_json


def criar_pasta_nova(pasta_da_analise: Path) -> None:
    pasta_da_analise.parent.mkdir(parents=True, exist_ok=True)
    try:
        pasta_da_analise.mkdir()
    except FileExistsError as erro:
        raise RelatorioJaExiste(pasta_da_analise) from erro
