import pytest

from rastro.versao_semver import versao_na_faixa


def test_r21_7_faixa_com_inicio_e_fim_contem_a_versao_do_meio() -> None:
    assert versao_na_faixa("3.4.1", ">= 1.2.0, < 3.5.0")


def test_r21_7_faixa_com_fim_aberto_nao_contem_o_proprio_fim() -> None:
    assert not versao_na_faixa("3.5.0", ">= 1.2.0, < 3.5.0")


def test_r21_7_faixa_contem_o_proprio_inicio_fechado() -> None:
    assert versao_na_faixa("1.2.0", ">= 1.2.0, < 3.5.0")


def test_r21_7_versao_abaixo_do_inicio_fica_fora() -> None:
    assert not versao_na_faixa("1.1.9", ">= 1.2.0, < 3.5.0")


def test_r21_7_versao_com_dois_numeros_vale_com_zero_no_fim() -> None:
    assert versao_na_faixa("1.2.0", ">= 1.2, < 3.5.0")


@pytest.mark.parametrize(
    ("versao", "faixa", "esperado"),
    [
        ("2.1.0", "<= 2.1.0", True),
        ("2.1.1", "<= 2.1.0", False),
        ("1.0.2", "< 1.0.3", True),
        ("4.0.0", "> 3.9.9", True),
        ("3.9.9", "> 3.9.9", False),
        ("2.1.0", ">= 1.0.0, <= 2.1.0", True),
        ("2.1.0", "= 2.1.0", True),
        ("2.1.0", "2.1.0", True),
        ("2.1.1", "= 2.1.0", False),
        ("10.0.0", "< 9.0.0", False),
    ],
)
def test_r21_7_operadores_da_faixa(versao: str, faixa: str, esperado: bool) -> None:
    assert versao_na_faixa(versao, faixa) is esperado


def test_r21_7_pre_lancamento_e_menor_que_a_versao_final() -> None:
    assert versao_na_faixa("3.5.0-beta.1", ">= 1.2.0, < 3.5.0")


def test_r21_7_versao_final_nao_cabe_antes_do_pre_lancamento() -> None:
    assert not versao_na_faixa("3.5.0", "< 3.5.0-rc.1")


@pytest.mark.parametrize(
    ("menor", "maior"),
    [
        ("1.0.0-alpha", "1.0.0-alpha.1"),
        ("1.0.0-alpha.1", "1.0.0-beta"),
        ("1.0.0-beta.2", "1.0.0-beta.11"),
        ("1.0.0-rc.1", "1.0.0"),
    ],
)
def test_r21_7_pre_lancamentos_seguem_a_ordem_do_semver(menor: str, maior: str) -> None:
    assert versao_na_faixa(menor, f"< {maior}")
    assert not versao_na_faixa(maior, f"< {menor}")


def test_r21_7_metadado_de_build_nao_conta_na_comparacao() -> None:
    assert versao_na_faixa("3.4.1+build.7", "= 3.4.1")
