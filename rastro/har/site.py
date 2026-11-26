from urllib.parse import urlsplit, urlunsplit

from rastro.har.modelos import Requisicao

MARCADOR_DA_QUERY_REMOVIDA = "[removido]"
PRIMEIRO_STATUS_DE_REDIRECIONAMENTO = 300
PRIMEIRO_STATUS_DE_ERRO = 400


def descobrir_site_analisado(requisicoes: list[Requisicao]) -> str | None:
    url_da_pagina = primeira_url_da_pagina(requisicoes)
    if url_da_pagina is not None:
        return host_com_porta(url_da_pagina)
    return host_da_primeira_pagina_html(requisicoes)


def primeira_url_da_pagina(requisicoes: list[Requisicao]) -> str | None:
    for requisicao in requisicoes:
        if requisicao.url_da_pagina:
            return requisicao.url_da_pagina
    return None


def host_da_primeira_pagina_html(requisicoes: list[Requisicao]) -> str | None:
    for requisicao in requisicoes:
        if requisicao_e_pagina_html(requisicao):
            return host_com_porta(requisicao.url)
    return None


def requisicao_e_pagina_html(requisicao: Requisicao) -> bool:
    return requisicao.tipo_conteudo == "text/html" and not requisicao_e_redirecionamento(requisicao)


def requisicao_e_redirecionamento(requisicao: Requisicao) -> bool:
    return PRIMEIRO_STATUS_DE_REDIRECIONAMENTO <= requisicao.status < PRIMEIRO_STATUS_DE_ERRO


def host_com_porta(url: str) -> str | None:
    endereco = urlsplit(url).netloc
    host = endereco.rsplit("@", 1)[-1].lower()
    return host or None


def url_sem_valores_da_query(url: str) -> str:
    partes = urlsplit(url)
    query = MARCADOR_DA_QUERY_REMOVIDA if partes.query else ""
    return urlunsplit((partes.scheme, partes.netloc, partes.path, query, ""))


def url_sem_query_string(url: str) -> str:
    partes = urlsplit(url)
    return urlunsplit((partes.scheme, partes.netloc, partes.path, "", ""))
