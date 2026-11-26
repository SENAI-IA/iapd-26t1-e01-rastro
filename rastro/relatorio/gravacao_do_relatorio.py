import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rastro.gravacao_segura import (
    PastaJaExiste,
    caminho_da_pasta_com_data,
    criar_pasta_nova,
    gravar_arquivo_novo,
)
from rastro.relatorio.pagina_do_relatorio import NOME_DO_HTML, ler_modelo, montar_html

ESPACOS_DE_RECUO_DO_JSON = 2
NOME_DO_JSON = "relatorio.json"


@dataclass(frozen=True)
class RelatorioGravado:
    json: Path
    html: Path


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


def caminho_do_relatorio(pasta_dos_relatorios: Path, aplicacao: str, momento: datetime) -> Path:
    return caminho_da_pasta_com_data(pasta_dos_relatorios, aplicacao, momento)


def gravar_relatorio(pasta_da_analise: Path, relatorio: dict[str, Any]) -> RelatorioGravado:
    texto_do_json = (
        json.dumps(relatorio, ensure_ascii=False, indent=ESPACOS_DE_RECUO_DO_JSON) + "\n"
    )
    texto_do_html = montar_html(ler_modelo(), relatorio)
    criar_pasta_da_analise(pasta_da_analise)
    arquivos_gravados = RelatorioGravado(
        pasta_da_analise / NOME_DO_JSON, pasta_da_analise / NOME_DO_HTML
    )
    gravar_arquivo_novo(arquivos_gravados.json, texto_do_json)
    gravar_arquivo_novo(arquivos_gravados.html, texto_do_html)
    return arquivos_gravados


def criar_pasta_da_analise(pasta_da_analise: Path) -> None:
    try:
        criar_pasta_nova(pasta_da_analise)
    except PastaJaExiste as erro:
        raise RelatorioJaExiste(pasta_da_analise) from erro
