import pytest

from rastro.captura.endereco_da_visita import (
    UrlInvalida,
    entre_colchetes_se_for_ipv6,
    host_da_url,
    motivo_sem_usuario_e_senha,
    url_sem_usuario_e_senha,
)


@pytest.mark.parametrize(
    ("url", "host"),
    [
        ("https://Loja.Exemplo.com/produtos?id=1", "loja.exemplo.com"),
        ("http://127.0.0.1:8080/WebGoat/start.mvc", "127.0.0.1:8080"),
        ("https://loja.exemplo.com:443/", "loja.exemplo.com"),
        ("http://loja.exemplo.com:80/", "loja.exemplo.com"),
        ("https://[::1]:8443/", "[::1]:8443"),
    ],
)
def test_r24_2_aceita_url_http_e_https(url: str, host: str) -> None:
    assert host_da_url(url) == host


def test_r24_6_usuario_e_senha_da_url_nao_vao_para_o_host() -> None:
    assert host_da_url("https://ana:segredo@loja.exemplo.com:8443/") == "loja.exemplo.com:8443"


def test_r24_6_url_mostrada_sem_usuario_e_senha() -> None:
    assert (
        url_sem_usuario_e_senha("https://ana:segredo@loja.exemplo.com/painel?x=1")
        == "https://loja.exemplo.com/painel?x=1"
    )
    assert url_sem_usuario_e_senha("https://loja.exemplo.com/") == "https://loja.exemplo.com/"


@pytest.mark.parametrize(
    "url",
    ["loja.exemplo.com", "ftp://loja.exemplo.com", "https://", "", "https://loja.exemplo.com:abc/"],
)
def test_r24_2_recusa_url_sem_http_ou_https(url: str) -> None:
    with pytest.raises(UrlInvalida, match="http:// ou https://"):
        host_da_url(url)


def test_r24_2_host_ipv6_fica_entre_colchetes() -> None:
    assert entre_colchetes_se_for_ipv6("::1") == "[::1]"
    assert entre_colchetes_se_for_ipv6("loja.exemplo.com") == "loja.exemplo.com"


def test_r24_6_motivo_da_falha_sai_sem_usuario_e_senha() -> None:
    url = "https://ana:segredo@loja.exemplo.com/"

    assert (
        motivo_sem_usuario_e_senha(f"net::ERR_CONNECTION_REFUSED at {url}", url)
        == "net::ERR_CONNECTION_REFUSED at https://loja.exemplo.com/"
    )
