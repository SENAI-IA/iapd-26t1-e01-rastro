from rastro.configuracao.avaliacao_do_site import (
    checar_cookies_do_site,
    checar_paginas_do_site,
    montar_checagem,
    nao_verificada,
    nomes_dos_cookies,
    paginas_html_do_site,
    requisicao_e_do_site,
    respostas_do_site_com_cookies,
    usa_https,
)
from rastro.configuracao.modelos import RegraDeChecagem
from rastro.configuracao.regras_das_checagens import MOTIVO_SEM_COOKIES, MOTIVO_SEM_PAGINAS_HTML
from rastro.har.modelos import Cookie, Requisicao
from rastro.identificacao.modelos import Evidencia

SITE = "loja.exemplo"
REGRA = RegraDeChecagem("C99", "regra de teste", "baixa", "infra")
COOKIE_BOM = Cookie("bom", http_only=True, secure=True, same_site="Lax")
COOKIE_RUIM = Cookie("ruim", http_only=False, secure=True, same_site="Lax")


def resposta(
    indice: int,
    url: str = f"https://{SITE}/",
    tipo_conteudo: str = "text/html",
    cookies: list[Cookie] | None = None,
) -> Requisicao:
    return Requisicao(
        indice=indice,
        url=url,
        metodo="GET",
        status=200,
        tipo_conteudo=tipo_conteudo,
        cabecalhos_resposta={},
        cookies_resposta=cookies or [],
        conteudo=None,
    )


def sem_httponly(cookie: Cookie) -> bool:
    return not cookie.http_only


def test_r06_1_paginas_html_do_site_ignora_script_e_outro_host() -> None:
    pagina = resposta(0)
    script = resposta(1, f"https://{SITE}/app.js", "text/javascript")
    de_outro_host = resposta(2, "https://cdn.exemplo/")

    assert paginas_html_do_site([pagina, script, de_outro_host], SITE) == [pagina]


def test_r06_7_respostas_do_site_com_cookies_ignora_resposta_sem_cookie() -> None:
    com_cookie = resposta(0, cookies=[COOKIE_BOM])

    assert respostas_do_site_com_cookies([resposta(1), com_cookie], SITE) == [com_cookie]


def test_r06_1_sem_site_analisado_nada_e_do_site() -> None:
    assert requisicao_e_do_site(resposta(0), None) is False
    assert requisicao_e_do_site(resposta(0), SITE) is True


def test_r06_2_usa_https_olha_o_esquema_da_url() -> None:
    assert usa_https(resposta(0, "HTTPS://loja.exemplo/")) is True
    assert usa_https(resposta(0, "http://loja.exemplo/")) is False


def test_r06_8_pagina_que_falha_vira_evidencia_com_o_trecho() -> None:
    paginas = [resposta(0), resposta(1, f"https://{SITE}/conta?token=1")]

    checagem = checar_paginas_do_site(
        REGRA, paginas, lambda pagina: pagina.indice == 1, "falhou aqui", lambda _: "trecho"
    )

    assert checagem.situacao == "falhou"
    assert checagem.evidencia == Evidencia(1, f"https://{SITE}/conta?token=1", "trecho")
    assert checagem.detalhe == f"falhou aqui: https://{SITE}/conta"


def test_r06_8_paginas_que_passam_trazem_a_primeira_como_evidencia() -> None:
    checagem = checar_paginas_do_site(REGRA, [resposta(0), resposta(1)], lambda _: False, "x")

    assert checagem.situacao == "passou"
    assert checagem.evidencia == Evidencia(0, f"https://{SITE}/", None)
    assert checagem.detalhe == "as 2 respostas HTML do site conferidas passaram"


def test_r06_1_sem_paginas_nao_verificada() -> None:
    checagem = checar_paginas_do_site(REGRA, [], lambda _: True, "x")

    assert checagem.situacao == "nao_verificada"
    assert checagem.detalhe == MOTIVO_SEM_PAGINAS_HTML


def test_r06_6_cookies_que_falham_aparecem_pelo_nome() -> None:
    respostas = [resposta(0, cookies=[COOKIE_BOM]), resposta(1, cookies=[COOKIE_RUIM])]

    checagem = checar_cookies_do_site(REGRA, respostas, sem_httponly, "cookies sem HttpOnly")

    assert checagem.situacao == "falhou"
    assert checagem.evidencia == Evidencia(1, f"https://{SITE}/", "cookie: ruim")
    assert checagem.detalhe == "cookies sem HttpOnly: ruim"


def test_r06_6_cookies_que_passam_sao_contados_uma_vez() -> None:
    respostas = [resposta(0, cookies=[COOKIE_BOM]), resposta(1, cookies=[COOKIE_BOM])]

    checagem = checar_cookies_do_site(REGRA, respostas, sem_httponly, "x")

    assert checagem.situacao == "passou"
    assert checagem.detalhe == "os 1 cookies do site conferidos passaram"


def test_r06_7_sem_cookies_nao_verificada() -> None:
    checagem = checar_cookies_do_site(REGRA, [], sem_httponly, "x")

    assert checagem.situacao == "nao_verificada"
    assert checagem.detalhe == MOTIVO_SEM_COOKIES


def test_r06_6_nomes_dos_cookies_sem_repetir() -> None:
    respostas = [resposta(0, cookies=[COOKIE_RUIM, COOKIE_BOM]), resposta(1, cookies=[COOKIE_RUIM])]

    assert nomes_dos_cookies(respostas, sem_httponly) == ["ruim"]


def test_r06_8_checagem_traz_os_dados_da_regra() -> None:
    evidencia = Evidencia(0, f"https://{SITE}/", None)

    checagem = montar_checagem(REGRA, "passou", evidencia, "detalhe")

    assert (checagem.id, checagem.titulo, checagem.severidade, checagem.quem_resolve) == (
        "C99",
        "regra de teste",
        "baixa",
        "infra",
    )
    assert checagem.evidencia == evidencia


def test_r06_7_nao_verificada_fica_sem_evidencia() -> None:
    checagem = nao_verificada(REGRA, "motivo")

    assert checagem.situacao == "nao_verificada"
    assert checagem.evidencia is None
    assert checagem.detalhe == "motivo"
