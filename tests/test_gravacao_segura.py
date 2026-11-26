import pytest

from rastro.gravacao_segura import nome_de_pasta_seguro

CARACTERES_PROIBIDOS_NO_WINDOWS = '<>:"/\\|?*'


def test_r13_3_porta_vira_sublinhado() -> None:
    assert nome_de_pasta_seguro("localhost:3000") == "localhost_3000"


@pytest.mark.parametrize("caractere", list(CARACTERES_PROIBIDOS_NO_WINDOWS))
def test_r13_3_caractere_proibido_no_windows_vira_sublinhado(caractere: str) -> None:
    assert nome_de_pasta_seguro(f"site{caractere}x") == "site_x"


def test_r13_3_ponto_e_espaco_no_fim_saem() -> None:
    assert nome_de_pasta_seguro("site. ") == "site"


def test_r13_3_nome_vazio_ou_so_pontos_nao_sobe_de_pasta() -> None:
    assert nome_de_pasta_seguro("") == "_"
    assert nome_de_pasta_seguro("..") == "_"


@pytest.mark.parametrize("reservado", ["CON", "nul", "COM1", "lpt9.har"])
def test_r13_3_nome_reservado_do_windows_ganha_prefixo(reservado: str) -> None:
    assert nome_de_pasta_seguro(reservado) == f"_{reservado}"
