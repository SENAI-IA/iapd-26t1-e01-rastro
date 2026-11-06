from rastro.har.modelos import Requisicao
from rastro.har.site import descobrir_site_analisado


def requisicao(url: str, tipo_conteudo: str | None, status: int = 200) -> Requisicao:
    return Requisicao(
        indice=0,
        url=url,
        metodo="GET",
        status=status,
        tipo_conteudo=tipo_conteudo,
        cabecalhos_resposta={},
        cookies_resposta=[],
        conteudo=None,
    )


def test_r01_7_site_e_o_host_da_primeira_resposta_html() -> None:
    requisicoes = [
        requisicao("https://cdn.exemplo.net/jquery.min.js", "application/javascript"),
        requisicao("https://loja.exemplo.com.br/", "text/html"),
        requisicao("https://anuncios.exemplo.org/quadro.html", "text/html"),
    ]

    assert descobrir_site_analisado(requisicoes) == "loja.exemplo.com.br"


def test_r01_7_ignora_o_redirecionamento_e_usa_a_pagina_de_destino() -> None:
    requisicoes = [
        requisicao("http://exemplo.com.br/", "text/html", status=301),
        requisicao("https://www.exemplo.com.br/", "text/html"),
    ]

    assert descobrir_site_analisado(requisicoes) == "www.exemplo.com.br"


def test_r01_7_mantem_a_porta_e_usa_minusculas() -> None:
    requisicoes = [requisicao("http://Usuario@LocalHost:3000/", "text/html")]

    assert descobrir_site_analisado(requisicoes) == "localhost:3000"


def test_r01_7_resposta_de_erro_em_html_tambem_conta() -> None:
    requisicoes = [requisicao("https://loja.exemplo.com.br/nao-existe", "text/html", status=404)]

    assert descobrir_site_analisado(requisicoes) == "loja.exemplo.com.br"


def test_r01_7_har_sem_html_devolve_none() -> None:
    requisicoes = [
        requisicao("https://loja.exemplo.com.br/app.js", "application/javascript"),
        requisicao("wss://loja.exemplo.com.br/socket", None, status=101),
    ]

    assert descobrir_site_analisado(requisicoes) is None


def test_r01_7_har_vazio_devolve_none() -> None:
    assert descobrir_site_analisado([]) is None


def test_r01_7_html_sem_host_na_url_devolve_none() -> None:
    assert descobrir_site_analisado([requisicao("about:blank", "text/html")]) is None
