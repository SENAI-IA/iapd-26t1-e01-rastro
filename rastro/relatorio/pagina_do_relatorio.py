import json
from importlib import resources
from pathlib import Path
from typing import Any

NOME_DO_HTML = "relatorio.html"
TAG_DOS_DADOS_VAZIA = '<script id="dados" type="application/json"></script>'


class ModeloSemTagDosDados(Exception):
    def __init__(self) -> None:
        super().__init__(
            f"o modelo do relatório não traz a tag {TAG_DOS_DADOS_VAZIA} uma única vez. "
            "Refaça o build do frontend e copie o index.html para rastro/relatorio/modelo.html."
        )


def caminho_do_modelo() -> Path:
    return Path(str(resources.files("rastro.relatorio").joinpath("modelo.html"))).resolve()


def ler_modelo() -> str:
    return caminho_do_modelo().read_text(encoding="utf-8")


def montar_html(modelo: str, relatorio: dict[str, Any]) -> str:
    if modelo.count(TAG_DOS_DADOS_VAZIA) != 1:
        raise ModeloSemTagDosDados()
    tag_com_os_dados = TAG_DOS_DADOS_VAZIA.replace("></", f">{json_seguro_no_html(relatorio)}</")
    return modelo.replace(TAG_DOS_DADOS_VAZIA, tag_com_os_dados)


def json_seguro_no_html(relatorio: dict[str, Any]) -> str:
    return json.dumps(relatorio, ensure_ascii=False).replace("<", "\\u003c")
