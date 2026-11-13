from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from rastro.relatorio.gravacao import FORMATO_DA_PASTA_DA_ANALISE, nome_de_pasta_seguro

NOME_DO_HAR = "visita.har"
ESQUEMAS_ACEITOS = ("http", "https")


class UrlInvalida(Exception):
    def __init__(self, url: str) -> None:
        super().__init__(
            f"a URL precisa começar com http:// ou https://, como https://site.com.br: {url}"
        )


class GravacaoJaExiste(Exception):
    def __init__(self, pasta: Path) -> None:
        super().__init__(
            f"a pasta da gravação já existe: {pasta}. "
            "Nada foi gravado: o Rastro nunca sobrescreve uma gravação."
        )


def pasta_padrao_das_gravacoes() -> Path:
    return Path.home() / "Rastro" / "gravacoes"


def host_da_url(url: str) -> str:
    partes = urlsplit(url)
    if partes.scheme not in ESQUEMAS_ACEITOS or not partes.netloc:
        raise UrlInvalida(url)
    return partes.netloc.lower()


def caminho_da_gravacao(raiz: Path, host: str, momento: datetime) -> Path:
    return raiz / nome_de_pasta_seguro(host) / momento.strftime(FORMATO_DA_PASTA_DA_ANALISE)


def criar_pasta_da_gravacao(pasta: Path) -> Path:
    pasta.parent.mkdir(parents=True, exist_ok=True)
    try:
        pasta.mkdir()
    except FileExistsError as erro:
        raise GravacaoJaExiste(pasta) from erro
    return pasta / NOME_DO_HAR
