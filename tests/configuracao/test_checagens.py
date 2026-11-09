from collections.abc import Callable
from pathlib import Path

import pytest

from rastro.configuracao.checagens import (
    CHECAGENS,
    checar_configuracao,
    checar_cookie_sem_httponly,
    checar_cookie_sem_samesite,
    checar_cookie_sem_secure,
    checar_csp,
    checar_hsts,
    checar_nosniff,
    checar_protecao_contra_frame,
    checar_versao_do_servidor,
)
from rastro.configuracao.modelos import Checagem
from rastro.har.leitor import ler_har
from rastro.har.modelos import Cookie, Requisicao
from rastro.har.site import descobrir_site_analisado

SITE = "loja.exemplo:8443"
RAIZ_DO_PROJETO = Path(__file__).resolve().parents[2]
COOKIE_SEGURO = Cookie("sessao", http_only=True, secure=True, same_site="Lax")

CABECALHOS_SEGUROS = {
    "content-security-policy": "default-src 'self'",
    "strict-transport-security": "max-age=31536000",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "server": "nginx",
}

Checar = Callable[[list[Requisicao], str | None], Checagem]

TODAS_AS_CHECAGENS: list[Checar] = [
    checar_csp,
    checar_hsts,
    checar_nosniff,
    checar_protecao_contra_frame,
    checar_versao_do_servidor,
]

CHECAGENS_DE_COOKIE: list[Checar] = [
    checar_cookie_sem_httponly,
    checar_cookie_sem_secure,
    checar_cookie_sem_samesite,
]


def resposta(
    indice: int,
    cabecalhos: dict[str, str],
    url: str = f"https://{SITE}/",
    tipo_conteudo: str = "text/html",
    status: int = 200,
    cookies: list[Cookie] | None = None,
) -> Requisicao:
    return Requisicao(
        indice=indice,
        url=url,
        metodo="GET",
        status=status,
        tipo_conteudo=tipo_conteudo,
        cabecalhos_resposta=cabecalhos,
        cookies_resposta=cookies or [],
        conteudo=None,
    )


def sem(nome: str) -> dict[str, str]:
    cabecalhos = dict(CABECALHOS_SEGUROS)
    del cabecalhos[nome]
    return cabecalhos


def com(nome: str, valor: str) -> dict[str, str]:
    return {**CABECALHOS_SEGUROS, nome: valor}


@pytest.mark.parametrize("checar", TODAS_AS_CHECAGENS)
def test_r06_1_a_5_pagina_com_todos_os_cabecalhos_passa(checar: Checar) -> None:
    checagem = checar([resposta(0, CABECALHOS_SEGUROS)], SITE)

    assert checagem.situacao == "passou"


@pytest.mark.parametrize("checar", TODAS_AS_CHECAGENS)
def test_r06_1_a_5_sem_pagina_html_do_site_nao_verificada(checar: Checar) -> None:
    script = resposta(0, {}, tipo_conteudo="application/javascript")

    checagem = checar([script], SITE)

    assert checagem.situacao == "nao_verificada"
    assert checagem.evidencia is None


@pytest.mark.parametrize("checar", TODAS_AS_CHECAGENS)
def test_r06_1_a_5_resposta_de_outro_host_nao_conta(checar: Checar) -> None:
    pagina_do_site = resposta(0, CABECALHOS_SEGUROS)
    pagina_de_terceiro = resposta(1, {"server": "Apache/2.4.41"}, url="https://anuncios.exemplo/")

    checagem = checar([pagina_do_site, pagina_de_terceiro], SITE)

    assert checagem.situacao == "passou"


def test_r06_1_csp_ausente_falha() -> None:
    checagem = checar_csp([resposta(0, sem("content-security-policy"))], SITE)

    assert checagem.situacao == "falhou"
    assert checagem.titulo == "CSP ausente"


def test_r06_1_csp_so_report_only_falha() -> None:
    cabecalhos = sem("content-security-policy")
    cabecalhos["content-security-policy-report-only"] = "default-src 'self'"

    checagem = checar_csp([resposta(0, cabecalhos)], SITE)

    assert checagem.situacao == "falhou"


def test_r06_1_falha_se_alguma_pagina_falha_e_evidencia_e_a_primeira() -> None:
    requisicoes = [
        resposta(0, CABECALHOS_SEGUROS),
        resposta(1, sem("content-security-policy"), url=f"https://{SITE}/conta"),
        resposta(2, sem("content-security-policy"), url=f"https://{SITE}/sobre"),
    ]

    checagem = checar_csp(requisicoes, SITE)

    assert checagem.situacao == "falhou"
    assert checagem.evidencia is not None
    assert checagem.evidencia.indice_requisicao == 1
    assert checagem.evidencia.url == f"https://{SITE}/conta"


def test_r06_1_redirecionamento_e_script_sem_csp_nao_contam() -> None:
    requisicoes = [
        resposta(0, {}, status=302),
        resposta(1, CABECALHOS_SEGUROS),
        resposta(2, {}, url=f"https://{SITE}/app.js", tipo_conteudo="application/javascript"),
    ]

    checagem = checar_csp(requisicoes, SITE)

    assert checagem.situacao == "passou"


def test_r06_2_hsts_ausente_em_https_falha() -> None:
    checagem = checar_hsts([resposta(0, sem("strict-transport-security"))], SITE)

    assert checagem.situacao == "falhou"
    assert checagem.titulo == "HSTS ausente"


def test_r06_2_site_so_em_http_nao_verificada() -> None:
    pagina = resposta(0, sem("strict-transport-security"), url=f"http://{SITE}/")

    checagem = checar_hsts([pagina], SITE)

    assert checagem.situacao == "nao_verificada"
    assert "HTTPS" in checagem.detalhe


def test_r06_2_pagina_em_http_nao_conta_quando_o_site_usa_https() -> None:
    requisicoes = [
        resposta(0, sem("strict-transport-security"), url=f"http://{SITE}/"),
        resposta(1, CABECALHOS_SEGUROS),
    ]

    checagem = checar_hsts(requisicoes, SITE)

    assert checagem.situacao == "passou"


def test_r06_3_nosniff_ausente_falha() -> None:
    checagem = checar_nosniff([resposta(0, sem("x-content-type-options"))], SITE)

    assert checagem.situacao == "falhou"


def test_r06_3_valor_diferente_de_nosniff_falha() -> None:
    pagina = resposta(0, com("x-content-type-options", "sniff"))

    checagem = checar_nosniff([pagina], SITE)

    assert checagem.situacao == "falhou"


def test_r06_3_nosniff_em_maiusculas_passa() -> None:
    pagina = resposta(0, com("x-content-type-options", " NoSniff "))

    checagem = checar_nosniff([pagina], SITE)

    assert checagem.situacao == "passou"


def test_r06_4_sem_x_frame_options_e_sem_frame_ancestors_falha() -> None:
    checagem = checar_protecao_contra_frame([resposta(0, sem("x-frame-options"))], SITE)

    assert checagem.situacao == "falhou"
    assert checagem.titulo == "proteção contra frame ausente"


@pytest.mark.parametrize(
    "politica",
    [
        "default-src 'self'; frame-ancestors 'none'",
        "frame-ancestors 'self'",
        "default-src 'self', Frame-Ancestors https://painel.exemplo",
    ],
)
def test_r06_4_frame_ancestors_na_csp_passa(politica: str) -> None:
    cabecalhos = sem("x-frame-options")
    cabecalhos["content-security-policy"] = politica

    checagem = checar_protecao_contra_frame([resposta(0, cabecalhos)], SITE)

    assert checagem.situacao == "passou"


def test_r06_4_frame_ancestors_so_no_valor_de_outra_diretiva_falha() -> None:
    cabecalhos = sem("x-frame-options")
    cabecalhos["content-security-policy"] = "default-src https://frame-ancestors.exemplo"

    checagem = checar_protecao_contra_frame([resposta(0, cabecalhos)], SITE)

    assert checagem.situacao == "falhou"


@pytest.mark.parametrize(
    ("nome", "valor"),
    [
        ("server", "Apache/2.4.41 (Ubuntu)"),
        ("server", "Microsoft-IIS/10.0"),
        ("server", "nginx/1"),
        ("x-powered-by", "PHP/7.3.12"),
    ],
)
def test_r06_5_servidor_com_versao_falha(nome: str, valor: str) -> None:
    checagem = checar_versao_do_servidor([resposta(0, com(nome, valor))], SITE)

    assert checagem.situacao == "falhou"
    assert checagem.evidencia is not None
    assert checagem.evidencia.trecho == f"{nome}: {valor}"


@pytest.mark.parametrize(
    ("nome", "valor"),
    [("server", "nginx"), ("server", "cloudflare"), ("x-powered-by", "Express")],
)
def test_r06_5_servidor_sem_versao_passa(nome: str, valor: str) -> None:
    checagem = checar_versao_do_servidor([resposta(0, com(nome, valor))], SITE)

    assert checagem.situacao == "passou"


@pytest.mark.parametrize(
    ("checar", "id_da_checagem", "severidade"),
    [
        (checar_csp, "C01", "media"),
        (checar_hsts, "C02", "media"),
        (checar_nosniff, "C03", "baixa"),
        (checar_protecao_contra_frame, "C04", "baixa"),
        (checar_versao_do_servidor, "C05", "baixa"),
    ],
)
def test_r06_8_checagem_traz_severidade_quem_resolve_e_evidencia(
    checar: Checar, id_da_checagem: str, severidade: str
) -> None:
    checagem = checar([resposta(7, {})], SITE)

    assert checagem.id == id_da_checagem
    assert checagem.severidade == severidade
    assert checagem.quem_resolve == "infra"
    assert checagem.evidencia is not None
    assert checagem.evidencia.indice_requisicao == 7
    assert checagem.evidencia.url == f"https://{SITE}/"


def test_r06_8_passou_traz_a_primeira_pagina_conferida_como_evidencia() -> None:
    requisicoes = [resposta(3, CABECALHOS_SEGUROS), resposta(4, CABECALHOS_SEGUROS)]

    checagem = checar_csp(requisicoes, SITE)

    assert checagem.evidencia is not None
    assert checagem.evidencia.indice_requisicao == 3


def test_r06_1_sem_site_analisado_nao_verificada() -> None:
    checagem = checar_csp([resposta(0, {})], None)

    assert checagem.situacao == "nao_verificada"


def com_cookies(indice: int, *cookies: Cookie, url: str = f"https://{SITE}/api") -> Requisicao:
    return resposta(indice, {}, url=url, tipo_conteudo="application/json", cookies=list(cookies))


@pytest.mark.parametrize("checar", CHECAGENS_DE_COOKIE)
def test_r06_6_cookie_com_todos_os_atributos_passa(checar: Checar) -> None:
    checagem = checar([com_cookies(2, COOKIE_SEGURO)], SITE)

    assert checagem.situacao == "passou"
    assert checagem.evidencia is not None
    assert checagem.evidencia.indice_requisicao == 2


@pytest.mark.parametrize(
    ("checar", "cookie"),
    [
        (checar_cookie_sem_httponly, Cookie("sessao", False, True, "Lax")),
        (checar_cookie_sem_secure, Cookie("sessao", True, False, "Lax")),
        (checar_cookie_sem_samesite, Cookie("sessao", True, True, None)),
        (checar_cookie_sem_samesite, Cookie("sessao", True, True, " ")),
    ],
)
def test_r06_6_atributo_ausente_falha_com_o_nome_do_cookie(checar: Checar, cookie: Cookie) -> None:
    checagem = checar([com_cookies(4, COOKIE_SEGURO, cookie)], SITE)

    assert checagem.situacao == "falhou"
    assert checagem.evidencia is not None
    assert checagem.evidencia.indice_requisicao == 4
    assert checagem.evidencia.trecho == "cookie: sessao"
    assert checagem.detalhe.endswith(": sessao")


def test_r06_6_um_cookie_sem_httponly_nao_derruba_as_outras_checagens() -> None:
    sem_httponly = Cookie("preferencia", http_only=False, secure=True, same_site="Strict")
    requisicoes = [com_cookies(0, sem_httponly)]

    assert checar_cookie_sem_httponly(requisicoes, SITE).situacao == "falhou"
    assert checar_cookie_sem_secure(requisicoes, SITE).situacao == "passou"
    assert checar_cookie_sem_samesite(requisicoes, SITE).situacao == "passou"


def test_r06_6_lista_cada_cookie_que_falha_uma_vez_e_evidencia_e_a_primeira() -> None:
    sessao = Cookie("sessao", http_only=False, secure=True, same_site="Lax")
    rastreio = Cookie("rastreio", http_only=False, secure=True, same_site="Lax")
    requisicoes = [
        com_cookies(0, COOKIE_SEGURO),
        com_cookies(1, sessao),
        com_cookies(2, sessao, rastreio),
    ]

    checagem = checar_cookie_sem_httponly(requisicoes, SITE)

    assert checagem.detalhe == "cookies sem HttpOnly: sessao, rastreio"
    assert checagem.evidencia is not None
    assert checagem.evidencia.indice_requisicao == 1


@pytest.mark.parametrize("checar", CHECAGENS_DE_COOKIE)
def test_r06_6_cookie_de_outro_host_nao_conta(checar: Checar) -> None:
    inseguro = Cookie("anuncio", http_only=False, secure=False, same_site=None)
    requisicoes = [
        com_cookies(0, COOKIE_SEGURO),
        com_cookies(1, inseguro, url="https://anuncios.exemplo/pixel"),
    ]

    assert checar(requisicoes, SITE).situacao == "passou"


def test_r06_6_cookie_sem_secure_em_http_nao_conta_quando_o_site_usa_https() -> None:
    inseguro = Cookie("sessao", http_only=True, secure=False, same_site="Lax")
    requisicoes = [
        com_cookies(0, inseguro, url=f"http://{SITE}/"),
        com_cookies(1, COOKIE_SEGURO),
    ]

    assert checar_cookie_sem_secure(requisicoes, SITE).situacao == "passou"


def test_r06_6_site_so_em_http_deixa_secure_nao_verificada() -> None:
    inseguro = Cookie("sessao", http_only=True, secure=False, same_site="Lax")

    checagem = checar_cookie_sem_secure([com_cookies(0, inseguro, url=f"http://{SITE}/")], SITE)

    assert checagem.situacao == "nao_verificada"
    assert checagem.evidencia is None


@pytest.mark.parametrize(
    ("checar", "id_da_checagem", "severidade"),
    [
        (checar_cookie_sem_httponly, "C06", "media"),
        (checar_cookie_sem_secure, "C07", "media"),
        (checar_cookie_sem_samesite, "C08", "baixa"),
    ],
)
def test_r06_6_checagem_traz_severidade_e_quem_resolve(
    checar: Checar, id_da_checagem: str, severidade: str
) -> None:
    checagem = checar([com_cookies(0, Cookie("sessao", False, False, None))], SITE)

    assert checagem.id == id_da_checagem
    assert checagem.severidade == severidade
    assert checagem.quem_resolve == "dev back-end"


@pytest.mark.parametrize("checar", CHECAGENS_DE_COOKIE)
def test_r06_7_sem_cookies_do_site_nao_verificada_e_sugere_har_completo(checar: Checar) -> None:
    requisicoes = [resposta(0, CABECALHOS_SEGUROS)]

    checagem = checar(requisicoes, SITE)

    assert checagem.situacao == "nao_verificada"
    assert checagem.evidencia is None
    assert "HAR completo" in checagem.detalhe


@pytest.mark.parametrize("checar", CHECAGENS_DE_COOKIE)
def test_r06_7_sem_site_analisado_nao_verificada(checar: Checar) -> None:
    assert checar([com_cookies(0, COOKIE_SEGURO)], None).situacao == "nao_verificada"


@pytest.mark.parametrize("checar", CHECAGENS_DE_COOKIE)
def test_r06_7_har_sanitized_real_da_nao_verificada(checar: Checar) -> None:
    requisicoes = ler_har(RAIZ_DO_PROJETO / "avaliacao" / "webgoat.har")

    checagem = checar(requisicoes, descobrir_site_analisado(requisicoes))

    assert checagem.situacao == "nao_verificada"


def test_r06_6_valor_do_cookie_nunca_aparece_no_resultado() -> None:
    requisicoes = ler_har(RAIZ_DO_PROJETO / "tests" / "dados" / "har-valido.har")
    site = descobrir_site_analisado(requisicoes)

    checagens = [checar(requisicoes, site) for checar in CHECAGENS_DE_COOKIE]

    assert [checagem.situacao for checagem in checagens] == ["falhou", "falhou", "passou"]
    assert "idioma" in checagens[0].detalhe
    for checagem in checagens:
        assert "valor-ficticio" not in repr(checagem)
        assert "pt-BR" not in repr(checagem)


def test_r06_8_checar_configuracao_roda_todas_as_regras_na_ordem_dos_ids() -> None:
    requisicoes = ler_har(RAIZ_DO_PROJETO / "tests" / "dados" / "loja.har")

    checagens = checar_configuracao(requisicoes, descobrir_site_analisado(requisicoes))

    assert [checagem.id for checagem in checagens] == [f"C0{numero}" for numero in range(1, 9)]
    assert list(CHECAGENS) == TODAS_AS_CHECAGENS + CHECAGENS_DE_COOKIE
