from collections.abc import Callable
from dataclasses import replace

from rastro.configuracao.avaliacao_do_site import (
    checar_cookies_do_site,
    checar_paginas_do_site,
    nao_verificada,
    paginas_html_do_site,
    respostas_do_site_com_cookies,
    usa_https,
)
from rastro.configuracao.falhas_nos_cabecalhos import (
    cabecalho_que_mostra_versao,
    expoe_versao_do_servidor,
    sem_csp,
    sem_hsts,
    sem_nosniff,
    sem_protecao_contra_frame,
)
from rastro.configuracao.falhas_nos_cookies import sem_httponly, sem_samesite, sem_secure
from rastro.configuracao.modelos import Checagem
from rastro.configuracao.regras_das_checagens import (
    COOKIE_SEM_HTTPONLY,
    COOKIE_SEM_SAMESITE,
    COOKIE_SEM_SECURE,
    CSP_AUSENTE,
    FRAME_SEM_PROTECAO,
    HSTS_AUSENTE,
    IDS_DAS_CHECAGENS_DE_COOKIE,
    MOTIVO_SEM_COOKIES_NA_GRAVACAO,
    NOSNIFF_AUSENTE,
    SERVIDOR_EXPOE_VERSAO,
)
from rastro.har.modelos import Requisicao


def checar_csp(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        CSP_AUSENTE,
        paginas_html_do_site(requisicoes, site),
        sem_csp,
        "a página não envia Content-Security-Policy",
    )


def checar_hsts(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    paginas = paginas_html_do_site(requisicoes, site)
    paginas_em_https = [pagina for pagina in paginas if usa_https(pagina)]
    if paginas and not paginas_em_https:
        return nao_verificada(HSTS_AUSENTE, "o site não usa HTTPS; HSTS só vale em HTTPS")
    return checar_paginas_do_site(
        HSTS_AUSENTE,
        paginas_em_https,
        sem_hsts,
        "a página em HTTPS não envia Strict-Transport-Security",
    )


def checar_nosniff(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        NOSNIFF_AUSENTE,
        paginas_html_do_site(requisicoes, site),
        sem_nosniff,
        "a página não envia X-Content-Type-Options: nosniff",
    )


def checar_protecao_contra_frame(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        FRAME_SEM_PROTECAO,
        paginas_html_do_site(requisicoes, site),
        sem_protecao_contra_frame,
        "a página não envia X-Frame-Options nem frame-ancestors na CSP",
    )


def checar_versao_do_servidor(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        SERVIDOR_EXPOE_VERSAO,
        paginas_html_do_site(requisicoes, site),
        expoe_versao_do_servidor,
        "o cabeçalho mostra a versão do servidor",
        cabecalho_que_mostra_versao,
    )


def checar_cookie_sem_httponly(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_cookies_do_site(
        COOKIE_SEM_HTTPONLY,
        respostas_do_site_com_cookies(requisicoes, site),
        sem_httponly,
        "cookies sem HttpOnly",
    )


def checar_cookie_sem_secure(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    respostas = respostas_do_site_com_cookies(requisicoes, site)
    respostas_em_https = [resposta for resposta in respostas if usa_https(resposta)]
    if respostas and not respostas_em_https:
        return nao_verificada(COOKIE_SEM_SECURE, "o site não usa HTTPS; Secure só vale em HTTPS")
    return checar_cookies_do_site(
        COOKIE_SEM_SECURE,
        respostas_em_https,
        sem_secure,
        "cookies em HTTPS sem Secure",
    )


def checar_cookie_sem_samesite(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_cookies_do_site(
        COOKIE_SEM_SAMESITE,
        respostas_do_site_com_cookies(requisicoes, site),
        sem_samesite,
        "cookies sem SameSite",
    )


CHECAGENS: tuple[Callable[[list[Requisicao], str | None], Checagem], ...] = (
    checar_csp,
    checar_hsts,
    checar_nosniff,
    checar_protecao_contra_frame,
    checar_versao_do_servidor,
    checar_cookie_sem_httponly,
    checar_cookie_sem_secure,
    checar_cookie_sem_samesite,
)


def checar_configuracao(
    requisicoes: list[Requisicao], site: str | None, gravado_pelo_rastro: bool = False
) -> list[Checagem]:
    checagens = [checar(requisicoes, site) for checar in CHECAGENS]
    if not gravacao_sem_cookies(requisicoes, site, gravado_pelo_rastro):
        return checagens
    return [explicar_falta_de_cookie_na_gravacao(checagem) for checagem in checagens]


def gravacao_sem_cookies(
    requisicoes: list[Requisicao], site: str | None, gravado_pelo_rastro: bool
) -> bool:
    return gravado_pelo_rastro and not respostas_do_site_com_cookies(requisicoes, site)


def explicar_falta_de_cookie_na_gravacao(checagem: Checagem) -> Checagem:
    if checagem.id not in IDS_DAS_CHECAGENS_DE_COOKIE:
        return checagem
    return replace(checagem, detalhe=MOTIVO_SEM_COOKIES_NA_GRAVACAO)
