from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from rastro.relatorio.gravacao import FORMATO_DA_PASTA_DA_ANALISE, nome_de_pasta_seguro

NOME_DO_HAR = "visita.har"
ESQUEMAS_ACEITOS = ("http", "https")
PORTAS_PADRAO = {"http": 80, "https": 443}
PERMISSAO_SO_DO_DONO = 0o700


class UrlInvalida(Exception):
    def __init__(self, url: str) -> None:
        super().__init__(
            "a URL precisa começar com http:// ou https://, como https://site.com.br: "
            f"{url_sem_usuario_e_senha(url)}"
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
    if partes.scheme not in ESQUEMAS_ACEITOS or not partes.hostname:
        raise UrlInvalida(url)
    try:
        porta = partes.port
    except ValueError as erro:
        raise UrlInvalida(url) from erro
    host = entre_colchetes_se_for_ipv6(partes.hostname)
    if porta is None or porta == PORTAS_PADRAO[partes.scheme]:
        return host
    return f"{host}:{porta}"


def entre_colchetes_se_for_ipv6(host: str) -> str:
    if ":" in host:
        return f"[{host}]"
    return host


def url_sem_usuario_e_senha(url: str) -> str:
    partes = urlsplit(url)
    if partes.username is None and partes.password is None:
        return url
    return partes._replace(netloc=partes.netloc.rsplit("@", 1)[1]).geturl()


def caminho_da_gravacao(raiz: Path, host: str, momento: datetime) -> Path:
    return raiz / nome_de_pasta_seguro(host) / momento.strftime(FORMATO_DA_PASTA_DA_ANALISE)


def criar_pasta_da_gravacao(pasta: Path) -> Path:
    pasta.parent.mkdir(parents=True, exist_ok=True)
    try:
        pasta.mkdir(mode=PERMISSAO_SO_DO_DONO)
    except FileExistsError as erro:
        raise GravacaoJaExiste(pasta) from erro
    return pasta / NOME_DO_HAR


def desfazer_pasta_da_gravacao(pasta: Path) -> None:
    (pasta / NOME_DO_HAR).unlink(missing_ok=True)
    pasta.rmdir()
