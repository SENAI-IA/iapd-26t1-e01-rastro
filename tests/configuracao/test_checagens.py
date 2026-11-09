from collections.abc import Callable

import pytest

from rastro.configuracao.checagens import (
    checar_csp,
    checar_hsts,
    checar_nosniff,
    checar_protecao_contra_frame,
    checar_versao_do_servidor,
)
from rastro.configuracao.modelos import Checagem
from rastro.har.modelos import Requisicao

SITE = "loja.exemplo:8443"

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


def resposta(
    indice: int,
    cabecalhos: dict[str, str],
    url: str = f"https://{SITE}/",
    tipo_conteudo: str = "text/html",
    status: int = 200,
) -> Requisicao:
    return Requisicao(
        indice=indice,
        url=url,
        metodo="GET",
        status=status,
        tipo_conteudo=tipo_conteudo,
        cabecalhos_resposta=cabecalhos,
        cookies_resposta=[],
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
