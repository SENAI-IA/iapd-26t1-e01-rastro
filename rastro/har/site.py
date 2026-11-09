from urllib.parse import urlsplit, urlunsplit

from rastro.har.modelos import Requisicao


def descobrir_site_analisado(requisicoes: list[Requisicao]) -> str | None:
    for requisicao in requisicoes:
        if e_pagina_html(requisicao):
            return host_com_porta(requisicao.url)
    return None


def e_pagina_html(requisicao: Requisicao) -> bool:
    return requisicao.tipo_conteudo == "text/html" and not e_redirecionamento(requisicao)


def e_redirecionamento(requisicao: Requisicao) -> bool:
    return 300 <= requisicao.status < 400


def host_com_porta(url: str) -> str | None:
    endereco = urlsplit(url).netloc
    host = endereco.rsplit("@", 1)[-1].lower()
    return host or None


def url_sem_query_string(url: str) -> str:
    partes = urlsplit(url)
    return urlunsplit((partes.scheme, partes.netloc, partes.path, "", ""))
