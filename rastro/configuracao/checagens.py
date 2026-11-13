import re
from collections.abc import Callable
from dataclasses import replace
from urllib.parse import urlsplit

from rastro.configuracao.modelos import Checagem, RegraDeChecagem, SituacaoDaChecagem
from rastro.har.modelos import Cookie, Requisicao
from rastro.har.site import e_pagina_html, host_com_porta, url_sem_query_string
from rastro.identificacao.modelos import Evidencia

CSP_AUSENTE = RegraDeChecagem("C01", "CSP ausente", "media", "infra")
HSTS_AUSENTE = RegraDeChecagem("C02", "HSTS ausente", "media", "infra")
NOSNIFF_AUSENTE = RegraDeChecagem("C03", "nosniff ausente", "baixa", "infra")
FRAME_SEM_PROTECAO = RegraDeChecagem("C04", "proteção contra frame ausente", "baixa", "infra")
SERVIDOR_EXPOE_VERSAO = RegraDeChecagem("C05", "servidor expõe versão", "baixa", "infra")
COOKIE_SEM_HTTPONLY = RegraDeChecagem("C06", "cookie sem HttpOnly", "media", "dev back-end")
COOKIE_SEM_SECURE = RegraDeChecagem("C07", "cookie sem Secure", "media", "dev back-end")
COOKIE_SEM_SAMESITE = RegraDeChecagem("C08", "cookie sem SameSite", "baixa", "dev back-end")

CABECALHOS_DE_SERVIDOR = ("server", "x-powered-by")
PADRAO_DE_VERSAO = re.compile(r"\d+\.\d+|/v?\d+")
SEPARADOR_DE_DIRETIVAS_CSP = re.compile(r"[;,]")

MOTIVO_SEM_COOKIES = (
    "o HAR não traz cookies do site analisado (ex.: exportado no modo sanitized); "
    "exportar o HAR completo inclui as checagens de cookie C06 a C08"
)
MOTIVO_SEM_COOKIES_NA_GRAVACAO = (
    "o site não criou nenhum cookie durante a visita gravada pelo Rastro; "
    "a gravação guarda os cookies, então não há o que conferir"
)

TesteDeFalha = Callable[[Requisicao], bool]
TrechoDaEvidencia = Callable[[Requisicao], str | None]
TesteDeCookie = Callable[[Cookie], bool]


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
        cabecalhos_com_versao,
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
    if not gravado_pelo_rastro:
        return checagens
    return [explicar_falta_de_cookie_na_gravacao(checagem) for checagem in checagens]


def explicar_falta_de_cookie_na_gravacao(checagem: Checagem) -> Checagem:
    """A gravação do `gravar` guarda os cookies: sem eles, não há por que pedir o HAR completo."""
    if checagem.detalhe != MOTIVO_SEM_COOKIES:
        return checagem
    return replace(checagem, detalhe=MOTIVO_SEM_COOKIES_NA_GRAVACAO)


def respostas_do_site_com_cookies(
    requisicoes: list[Requisicao], site: str | None
) -> list[Requisicao]:
    respostas = []
    for requisicao in requisicoes:
        if requisicao.cookies_resposta and e_do_site(requisicao, site):
            respostas.append(requisicao)
    return respostas


def checar_cookies_do_site(
    regra: RegraDeChecagem,
    respostas: list[Requisicao],
    falha: TesteDeCookie,
    motivo_da_falha: str,
) -> Checagem:
    if not respostas:
        return nao_verificada(regra, MOTIVO_SEM_COOKIES)
    respostas_que_falham = [
        resposta for resposta in respostas if tem_cookie_que_falha(resposta, falha)
    ]
    if respostas_que_falham:
        nomes = nomes_dos_cookies(respostas_que_falham, falha)
        primeira = respostas_que_falham[0]
        evidencia = Evidencia(primeira.indice, primeira.url, f"cookie: {nomes[0]}")
        detalhe = f"{motivo_da_falha}: {', '.join(nomes)}"
        return montar_checagem(regra, "falhou", evidencia, detalhe)
    primeira = respostas[0]
    evidencia = Evidencia(primeira.indice, primeira.url, None)
    quantidade = len(nomes_dos_cookies(respostas, qualquer_cookie))
    detalhe = f"os {quantidade} cookies do site conferidos passaram"
    return montar_checagem(regra, "passou", evidencia, detalhe)


def tem_cookie_que_falha(resposta: Requisicao, falha: TesteDeCookie) -> bool:
    return any(falha(cookie) for cookie in resposta.cookies_resposta)


def nomes_dos_cookies(respostas: list[Requisicao], filtro: TesteDeCookie) -> list[str]:
    nomes: list[str] = []
    for resposta in respostas:
        for cookie in resposta.cookies_resposta:
            if filtro(cookie) and cookie.nome not in nomes:
                nomes.append(cookie.nome)
    return nomes


def paginas_html_do_site(requisicoes: list[Requisicao], site: str | None) -> list[Requisicao]:
    paginas = []
    for requisicao in requisicoes:
        if e_pagina_html(requisicao) and e_do_site(requisicao, site):
            paginas.append(requisicao)
    return paginas


def e_do_site(requisicao: Requisicao, site: str | None) -> bool:
    return site is not None and host_com_porta(requisicao.url) == site


def checar_paginas_do_site(
    regra: RegraDeChecagem,
    paginas: list[Requisicao],
    falha: TesteDeFalha,
    motivo_da_falha: str,
    trecho_da_evidencia: TrechoDaEvidencia | None = None,
) -> Checagem:
    if not paginas:
        return nao_verificada(regra, "nenhuma resposta HTML do site analisado no HAR")
    for pagina in paginas:
        if falha(pagina):
            trecho = None
            if trecho_da_evidencia is not None:
                trecho = trecho_da_evidencia(pagina)
            evidencia = Evidencia(pagina.indice, pagina.url, trecho)
            detalhe = f"{motivo_da_falha}: {url_sem_query_string(pagina.url)}"
            return montar_checagem(regra, "falhou", evidencia, detalhe)
    primeira = paginas[0]
    evidencia = Evidencia(primeira.indice, primeira.url, None)
    detalhe = f"as {len(paginas)} respostas HTML do site conferidas passaram"
    return montar_checagem(regra, "passou", evidencia, detalhe)


def montar_checagem(
    regra: RegraDeChecagem,
    situacao: SituacaoDaChecagem,
    evidencia: Evidencia,
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


def nao_verificada(regra: RegraDeChecagem, detalhe: str) -> Checagem:
    return Checagem(
        id=regra.id,
        titulo=regra.titulo,
        situacao="nao_verificada",
        severidade=regra.severidade,
        quem_resolve=regra.quem_resolve,
        evidencia=None,
        detalhe=detalhe,
    )


def cabecalho(requisicao: Requisicao, nome: str) -> str:
    return requisicao.cabecalhos_resposta.get(nome, "").strip()


def usa_https(requisicao: Requisicao) -> bool:
    return urlsplit(requisicao.url).scheme.lower() == "https"


def sem_csp(pagina: Requisicao) -> bool:
    return not cabecalho(pagina, "content-security-policy")


def sem_hsts(pagina: Requisicao) -> bool:
    return not cabecalho(pagina, "strict-transport-security")


def sem_nosniff(pagina: Requisicao) -> bool:
    return cabecalho(pagina, "x-content-type-options").lower() != "nosniff"


def sem_protecao_contra_frame(pagina: Requisicao) -> bool:
    return not cabecalho(pagina, "x-frame-options") and not csp_tem_frame_ancestors(pagina)


def csp_tem_frame_ancestors(pagina: Requisicao) -> bool:
    politica = cabecalho(pagina, "content-security-policy")
    for diretiva in SEPARADOR_DE_DIRETIVAS_CSP.split(politica):
        nome_da_diretiva = diretiva.strip().split(" ")[0].lower()
        if nome_da_diretiva == "frame-ancestors":
            return True
    return False


def expoe_versao_do_servidor(pagina: Requisicao) -> bool:
    return cabecalhos_com_versao(pagina) is not None


def cabecalhos_com_versao(pagina: Requisicao) -> str | None:
    for nome in CABECALHOS_DE_SERVIDOR:
        valor = cabecalho(pagina, nome)
        if PADRAO_DE_VERSAO.search(valor):
            return f"{nome}: {valor}"
    return None


def qualquer_cookie(_cookie: Cookie) -> bool:
    return True


def sem_httponly(cookie: Cookie) -> bool:
    return not cookie.http_only


def sem_secure(cookie: Cookie) -> bool:
    return not cookie.secure


def sem_samesite(cookie: Cookie) -> bool:
    return not (cookie.same_site or "").strip()
