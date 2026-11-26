import re
from urllib.parse import SplitResult, urldefrag, urlsplit, urlunsplit

from rastro.captura.endereco_da_visita import ESQUEMAS_ACEITOS, PORTAS_PADRAO

PALAVRAS_PERIGOSAS = re.compile(
    r"logout|log-out|signout|sign-out|sair|delete|excluir|remove|remover|uninstall|"
    r"cron|flush|reset|token=",
    re.IGNORECASE,
)
EXTENSOES_DE_ARQUIVO = re.compile(
    r"\.(pdf|zip|gz|tar|rar|7z|exe|msi|dmg|apk|png|jpe?g|gif|svg|webp|ico|mp4|mp3|"
    r"docx?|xlsx?|pptx?|csv)$",
    re.IGNORECASE,
)
URL_DENTRO_DA_QUERY = re.compile(r"https?:|https?%3a%2f%2f|%2f%2f", re.IGNORECASE)
PREFIXO_WWW = "www."


def url_para_comparar(url: str) -> str:
    sem_fragmento, fragmento = urldefrag(url)
    partes = urlsplit(sem_fragmento)
    rota = fragmento if fragmento_aponta_rota_de_spa(fragmento) else ""
    return urlunsplit(
        (
            partes.scheme,
            partes.netloc.lower(),
            partes.path or "/",
            nomes_dos_parametros_da_query(partes.query),
            rota,
        )
    )


def nomes_dos_parametros_da_query(query: str) -> str:
    nomes = [parametro.split("=", 1)[0] for parametro in query.split("&") if parametro]
    return "&".join(sorted(nomes))


def fragmento_aponta_rota_de_spa(fragmento: str) -> bool:
    return "/" in fragmento


def familia_da_pagina(url: str) -> str:
    _, fragmento = urldefrag(url)
    caminho = fragmento if fragmento_aponta_rota_de_spa(fragmento) else urlsplit(url).path
    trechos = [trecho for trecho in caminho.split("/") if trecho]
    if len(trechos) < 2:
        return "/" + "/".join(trechos)
    return "/" + "/".join(trechos[:-1])


def host_do_site(url: str) -> str:
    partes = urlsplit(url)
    host = (partes.hostname or "").removeprefix(PREFIXO_WWW)
    try:
        porta = partes.port
    except ValueError:
        return ""
    if porta is None or porta == PORTAS_PADRAO.get(partes.scheme):
        return host
    return f"{host}:{porta}"


def link_permitido(url: str, host: str) -> bool:
    partes = urlsplit(url)
    if partes.scheme not in ESQUEMAS_ACEITOS or host_do_site(url) != host:
        return False
    if tem_palavra_perigosa(partes) or leva_para_outro_endereco(partes.query):
        return False
    return not EXTENSOES_DE_ARQUIVO.search(partes.path)


def tem_palavra_perigosa(partes: SplitResult) -> bool:
    trecho_depois_do_host = f"{partes.path}?{partes.query}#{partes.fragment}"
    return PALAVRAS_PERIGOSAS.search(trecho_depois_do_host) is not None


def leva_para_outro_endereco(query: str) -> bool:
    return URL_DENTRO_DA_QUERY.search(query) is not None


def saida_do_site(endereco: str, host: str) -> str | None:
    if host_do_site(endereco) == host:
        return None
    destino = urlsplit(endereco).hostname or endereco
    return f"saiu do site: foi redirecionado para {destino}"
