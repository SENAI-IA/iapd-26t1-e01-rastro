from collections.abc import Callable
from urllib.parse import urlsplit

from rastro.configuracao.modelos import Checagem, RegraDeChecagem, SituacaoDaChecagem
from rastro.configuracao.regras_das_checagens import MOTIVO_SEM_COOKIES, MOTIVO_SEM_PAGINAS_HTML
from rastro.har.modelos import Cookie, Requisicao
from rastro.har.site import host_com_porta, requisicao_e_pagina_html, url_sem_query_string
from rastro.identificacao.modelos import Evidencia

TesteDeFalha = Callable[[Requisicao], bool]
TrechoDaEvidencia = Callable[[Requisicao], str | None]
TesteDeCookie = Callable[[Cookie], bool]


def paginas_html_do_site(requisicoes: list[Requisicao], site: str | None) -> list[Requisicao]:
    paginas = []
    for requisicao in requisicoes:
        if requisicao_e_pagina_html(requisicao) and requisicao_e_do_site(requisicao, site):
            paginas.append(requisicao)
    return paginas


def respostas_do_site_com_cookies(
    requisicoes: list[Requisicao], site: str | None
) -> list[Requisicao]:
    respostas = []
    for requisicao in requisicoes:
        if requisicao.cookies_resposta and requisicao_e_do_site(requisicao, site):
            respostas.append(requisicao)
    return respostas


def requisicao_e_do_site(requisicao: Requisicao, site: str | None) -> bool:
    return site is not None and host_com_porta(requisicao.url) == site


def usa_https(requisicao: Requisicao) -> bool:
    return urlsplit(requisicao.url).scheme.lower() == "https"


def checar_paginas_do_site(
    regra: RegraDeChecagem,
    paginas: list[Requisicao],
    teste_de_falha: TesteDeFalha,
    motivo_da_falha: str,
    trecho_da_evidencia: TrechoDaEvidencia | None = None,
) -> Checagem:
    if not paginas:
        return nao_verificada(regra, MOTIVO_SEM_PAGINAS_HTML)
    pagina_que_falha = primeira_pagina_que_falha(paginas, teste_de_falha)
    if pagina_que_falha is not None:
        return checagem_da_pagina_que_falhou(
            regra, pagina_que_falha, motivo_da_falha, trecho_da_evidencia
        )
    return checagem_das_paginas_que_passaram(regra, paginas)


def primeira_pagina_que_falha(
    paginas: list[Requisicao], teste_de_falha: TesteDeFalha
) -> Requisicao | None:
    for pagina in paginas:
        if teste_de_falha(pagina):
            return pagina
    return None


def checagem_da_pagina_que_falhou(
    regra: RegraDeChecagem,
    pagina: Requisicao,
    motivo_da_falha: str,
    trecho_da_evidencia: TrechoDaEvidencia | None,
) -> Checagem:
    trecho = None
    if trecho_da_evidencia is not None:
        trecho = trecho_da_evidencia(pagina)
    evidencia = Evidencia(pagina.indice, pagina.url, trecho)
    detalhe = f"{motivo_da_falha}: {url_sem_query_string(pagina.url)}"
    return montar_checagem(regra, "falhou", evidencia, detalhe)


def checagem_das_paginas_que_passaram(
    regra: RegraDeChecagem, paginas: list[Requisicao]
) -> Checagem:
    primeira = paginas[0]
    evidencia = Evidencia(primeira.indice, primeira.url, None)
    detalhe = f"as {len(paginas)} respostas HTML do site conferidas passaram"
    return montar_checagem(regra, "passou", evidencia, detalhe)


def checar_cookies_do_site(
    regra: RegraDeChecagem,
    respostas: list[Requisicao],
    teste_de_falha: TesteDeCookie,
    motivo_da_falha: str,
) -> Checagem:
    if not respostas:
        return nao_verificada(regra, MOTIVO_SEM_COOKIES)
    respostas_que_falham = respostas_com_cookie_que_falha(respostas, teste_de_falha)
    if respostas_que_falham:
        return checagem_dos_cookies_que_falharam(
            regra, respostas_que_falham, teste_de_falha, motivo_da_falha
        )
    return checagem_dos_cookies_que_passaram(regra, respostas)


def respostas_com_cookie_que_falha(
    respostas: list[Requisicao], teste_de_falha: TesteDeCookie
) -> list[Requisicao]:
    return [resposta for resposta in respostas if tem_cookie_que_falha(resposta, teste_de_falha)]


def tem_cookie_que_falha(resposta: Requisicao, teste_de_falha: TesteDeCookie) -> bool:
    return any(teste_de_falha(cookie) for cookie in resposta.cookies_resposta)


def checagem_dos_cookies_que_falharam(
    regra: RegraDeChecagem,
    respostas_que_falham: list[Requisicao],
    teste_de_falha: TesteDeCookie,
    motivo_da_falha: str,
) -> Checagem:
    nomes = nomes_dos_cookies(respostas_que_falham, teste_de_falha)
    primeira = respostas_que_falham[0]
    evidencia = Evidencia(primeira.indice, primeira.url, f"cookie: {nomes[0]}")
    detalhe = f"{motivo_da_falha}: {', '.join(nomes)}"
    return montar_checagem(regra, "falhou", evidencia, detalhe)


def checagem_dos_cookies_que_passaram(
    regra: RegraDeChecagem, respostas: list[Requisicao]
) -> Checagem:
    primeira = respostas[0]
    evidencia = Evidencia(primeira.indice, primeira.url, None)
    quantidade = len(nomes_dos_cookies(respostas, qualquer_cookie))
    detalhe = f"os {quantidade} cookies do site conferidos passaram"
    return montar_checagem(regra, "passou", evidencia, detalhe)


def nomes_dos_cookies(respostas: list[Requisicao], teste_do_cookie: TesteDeCookie) -> list[str]:
    nomes: list[str] = []
    for resposta in respostas:
        for cookie in resposta.cookies_resposta:
            if teste_do_cookie(cookie) and cookie.nome not in nomes:
                nomes.append(cookie.nome)
    return nomes


def qualquer_cookie(_cookie: Cookie) -> bool:
    return True


def nao_verificada(regra: RegraDeChecagem, detalhe: str) -> Checagem:
    return montar_checagem(regra, "nao_verificada", None, detalhe)


def montar_checagem(
    regra: RegraDeChecagem,
    situacao: SituacaoDaChecagem,
    evidencia: Evidencia | None,
    detalhe: str,
) -> Checagem:
    return Checagem(
        id=regra.id,
        titulo=regra.titulo,
        situacao=situacao,
        severidade=regra.severidade,
        quem_resolve=regra.quem_resolve,
        evidencia=evidencia,
        detalhe=detalhe,
    )
