import re
from urllib.parse import SplitResult, urldefrag, urlsplit, urlunsplit

from rastro.captura.endereco_da_visita import ESQUEMAS_ACEITOS, PORTAS_PADRAO

PALAVRAS_DE_ACAO_PERIGOSA = (
    "logout",
    "log-out",
    "signout",
    "sign-out",
    "sair",
    "delete",
    "excluir",
    "remove",
    "remover",
    "uninstall",
    "cron",
    "flush",
    "reset",
    "token=",
)
PALAVRAS_PERIGOSAS = re.compile("|".join(PALAVRAS_DE_ACAO_PERIGOSA), re.IGNORECASE)
EXTENSOES_DE_ARQUIVO = re.compile(
    r"""
    \.
    (?:
        pdf | zip | gz | tar | rar | 7z | exe | msi | dmg | apk
        | png | jpe?g | gif | svg | webp | ico
        | mp4 | mp3
        | docx? | xlsx? | pptx? | csv
    )
    $
    """,
    re.VERBOSE | re.IGNORECASE,
)
URL_DENTRO_DA_QUERY = re.compile(
    r"""
    https?:
    | https?%3a%2f%2f
    | %2f%2f
    """,
    re.VERBOSE | re.IGNORECASE,
)
PREFIXO_WWW = "www."
MINIMO_DE_TRECHOS_PARA_TER_PASTA = 2


def url_para_comparar(url: str) -> str:
    sem_fragmento, fragmento = urldefrag(url)
    partes = urlsplit(sem_fragmento)
    return urlunsplit(
        (
            partes.scheme,
            partes.netloc.lower(),
            caminho_ou_raiz(partes.path),
            nomes_dos_parametros_da_query(partes.query),
            rota_de_spa(fragmento),
        )
    )


def caminho_ou_raiz(caminho: str) -> str:
    if caminho:
        return caminho
    return "/"


def rota_de_spa(fragmento: str) -> str:
    if fragmento_aponta_rota_de_spa(fragmento):
        return fragmento
    return ""


def nomes_dos_parametros_da_query(query: str) -> str:
    nomes = []
    for parametro in query.split("&"):
        if parametro:
            nomes.append(nome_do_parametro(parametro))
    return "&".join(sorted(nomes))


def nome_do_parametro(parametro: str) -> str:
    nome, _, _ = parametro.partition("=")
    return nome


def fragmento_aponta_rota_de_spa(fragmento: str) -> bool:
    return "/" in fragmento


def familia_da_pagina(url: str) -> str:
    trechos = trechos_do_caminho(caminho_da_pagina(url))
    if len(trechos) < MINIMO_DE_TRECHOS_PARA_TER_PASTA:
        return "/" + "/".join(trechos)
    return "/" + "/".join(trechos[:-1])


def caminho_da_pagina(url: str) -> str:
    _, fragmento = urldefrag(url)
    if fragmento_aponta_rota_de_spa(fragmento):
        return fragmento
    return urlsplit(url).path


def trechos_do_caminho(caminho: str) -> list[str]:
    return [trecho for trecho in caminho.split("/") if trecho]


def host_do_site(url: str) -> str:
    partes = urlsplit(url)
    host = host_sem_www(partes)
    try:
        porta = partes.port
    except ValueError:
        return ""
    if porta is None or porta == PORTAS_PADRAO.get(partes.scheme):
        return host
    return f"{host}:{porta}"


def host_sem_www(partes: SplitResult) -> str:
    if partes.hostname is None:
        return ""
    return partes.hostname.removeprefix(PREFIXO_WWW)


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
    destino = urlsplit(endereco).hostname
    if not destino:
        destino = endereco
    return f"saiu do site: foi redirecionado para {destino}"
