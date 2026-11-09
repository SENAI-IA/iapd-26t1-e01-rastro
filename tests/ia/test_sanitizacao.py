import pytest

from rastro.ia.sanitizacao import sanitizar

JWT_FICTICIO = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0ZSJ9.ZmljdGljaW8tYXNzaW5hdHVyYS1kZS10ZXN0ZQ"


def test_r16_3_jwt_vira_removido() -> None:
    assert sanitizar(f"token = '{JWT_FICTICIO}';") == "token = '[removido]';"


def test_r16_3_jwt_curto_tambem_vira_removido() -> None:
    assert sanitizar("t='eyJhIjoxfQ.eyJiIjoyfQ.c2ln'") == "t='[removido]'"


@pytest.mark.parametrize(
    "cabecalho",
    [
        "Authorization: Bearer token-ficticio-de-teste-0001",
        "authorization: bearer token-ficticio-de-teste-0001",
        f"Authorization: Bearer {JWT_FICTICIO}",
    ],
)
def test_r16_3_bearer_e_o_token_viram_removido(cabecalho: str) -> None:
    assert sanitizar(cabecalho).lower() == "authorization: [removido]"


def test_r16_3_bearer_montado_no_codigo_fica_como_esta() -> None:
    trecho = "headers:{Authorization:`Bearer ${localStorage.getItem(`token`)}`}"

    assert sanitizar(trecho) == trecho


def test_r16_3_query_string_da_url_vira_removido() -> None:
    texto = "https://loja.exemplo/assets/main.js?v=3&sessao=abc123 carregado"

    assert sanitizar(texto) == "https://loja.exemplo/assets/main.js?[removido] carregado"


def test_r16_3_query_string_termina_na_aspa() -> None:
    texto = '"url": "https://loja.exemplo/api?token=x1", "status": 200'

    assert sanitizar(texto) == '"url": "https://loja.exemplo/api?[removido]", "status": 200'


def test_r16_3_url_sem_query_string_fica_como_esta() -> None:
    texto = "/*! jQuery v3.4.1 | (c) JS Foundation | jquery.org/license */ https://jquery.com/"

    assert sanitizar(texto) == texto


@pytest.mark.parametrize(
    "chave",
    [
        "588306aedba1de01388032d5f42a60159eea9228",
        "0x8343d2eb2B13A2495De435a1b15e85b98115Ce05",
        "chave_ficticia_0123456789abcdefABCDEF",
        "ZmljdGljaW8tY2hhdmUtYmFzZTY0LWRlLXRlc3Rl==",
    ],
)
def test_r16_3_chave_hexadecimal_ou_base64_longa_vira_removido(chave: str) -> None:
    assert sanitizar(f"chave: '{chave}'") == "chave: '[removido]'"


def test_r16_3_sequencia_de_32_caracteres_fica_como_esta() -> None:
    hash_de_32 = "d41d8cd98f00b204e9800998ecf8427e"

    assert sanitizar(hash_de_32) == hash_de_32


@pytest.mark.parametrize(
    "trecho",
    [
        "__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED",
        "https://github.com/twbs/bootstrap/blob/master/LICENSE",
        "modernizr.com/download/-details-inputtypes-touchevents-addtest-prefixes",
    ],
)
def test_r16_3_nome_longo_sem_digito_e_caminho_ficam_como_estao(trecho: str) -> None:
    assert sanitizar(trecho) == trecho


def test_r16_3_trecho_de_biblioteca_passa_intacto() -> None:
    trecho = '[`ng-version`,`22.2.2`],e.VERSION="22.2.2",o="5.3.3"'

    assert sanitizar(trecho) == trecho
