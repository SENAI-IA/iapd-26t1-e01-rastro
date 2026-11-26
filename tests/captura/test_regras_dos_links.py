import pytest

from rastro.captura.regras_dos_links import (
    familia_da_pagina,
    host_do_site,
    link_permitido,
    url_para_comparar,
)

INICIO = "https://loja.exemplo.com/"
HOST = "loja.exemplo.com"


@pytest.mark.parametrize(
    ("primeira", "segunda"),
    [
        ("https://loja.exemplo.com/busca?q=a&p=1", "https://loja.exemplo.com/busca?p=2&q=b"),
        ("https://loja.exemplo.com/sobre#equipe", "https://loja.exemplo.com/sobre"),
        ("https://Loja.Exemplo.com/sobre", "https://loja.exemplo.com/sobre"),
    ],
)
def test_r24_11_mesma_pagina_com_outros_valores_ou_ancora(primeira: str, segunda: str) -> None:
    assert url_para_comparar(primeira) == url_para_comparar(segunda)


def test_r24_11_rota_de_spa_no_fragmento_e_outra_pagina() -> None:
    assert url_para_comparar(f"{INICIO}#/produtos") != url_para_comparar(f"{INICIO}#/carrinho")


@pytest.mark.parametrize(
    ("url", "esperada"),
    [
        ("https://loja.exemplo.com/admin/blocos/rodape", "/admin/blocos"),
        ("https://loja.exemplo.com/admin/blocos/rodape/", "/admin/blocos"),
        ("http://127.0.0.1:8080/WebGoat/start.mvc#lesson/CSRF.lesson", "/lesson"),
        ("https://loja.exemplo.com/contato", "/contato"),
        ("https://loja.exemplo.com/", "/"),
    ],
)
def test_r24_13_familia_e_o_caminho_sem_o_ultimo_trecho(url: str, esperada: str) -> None:
    assert familia_da_pagina(url) == esperada


@pytest.mark.parametrize(
    "url",
    [
        "https://outro.exemplo.com/",
        "https://loja.exemplo.com:8443/",
        "mailto:contato@loja.exemplo.com",
        "javascript:void(0)",
        "https://loja.exemplo.com/user/logout",
        "https://loja.exemplo.com/sair",
        "https://loja.exemplo.com/node/1/delete",
        "https://loja.exemplo.com/pedidos/excluir/3",
        "https://loja.exemplo.com/admin/flush?token=abc",
        "https://loja.exemplo.com/admin/run-cron",
        "https://loja.exemplo.com/catalogo.PDF",
        "https://loja.exemplo.com/fotos/vitrine.jpg",
        "https://loja.exemplo.com/redirect?to=https://github.com/loja",
        "https://loja.exemplo.com/sair-para?url=https%3A%2F%2Foutro.exemplo.com",
    ],
)
def test_r24_12_nao_segue_link_perigoso_de_fora_ou_de_arquivo(url: str) -> None:
    assert not link_permitido(url, HOST)


def test_r24_12_palavra_perigosa_no_host_nao_barra_o_site() -> None:
    assert link_permitido("https://cronos.exemplo.com/produtos", "cronos.exemplo.com")
    assert not link_permitido("https://cronos.exemplo.com/run-cron", "cronos.exemplo.com")


@pytest.mark.parametrize(
    "url",
    [
        "https://loja.exemplo.com/",
        "https://www.loja.exemplo.com/",
        "https://LOJA.exemplo.com:443/",
        "https://ana:segredo@loja.exemplo.com/",
    ],
)
def test_r24_10_mesmo_site_com_ou_sem_www_e_com_a_porta_padrao(url: str) -> None:
    assert host_do_site(url) == HOST


def test_r24_10_porta_diferente_e_outro_site() -> None:
    assert host_do_site("http://127.0.0.1:8080/") == "127.0.0.1:8080"
    assert host_do_site("https://loja.exemplo.com:8443/") != HOST


def test_r24_10_segue_link_comum_do_mesmo_site() -> None:
    assert link_permitido("https://loja.exemplo.com/produtos?pagina=2", HOST)
