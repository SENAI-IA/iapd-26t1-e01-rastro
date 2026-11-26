import time

import pytest

from rastro.travas.strings_de_javascript import formas_escritas, strings_do_trecho

TRECHO_DO_ANGULAR = "[`ng-version`,`22.2.2`]"


@pytest.mark.parametrize(
    ("trecho", "esperado"),
    [
        (TRECHO_DO_ANGULAR, ["ng-version", "22.2.2"]),
        ('U$1=`FA "5.15.4"`', ['FA "5.15.4"']),
        ('"FA \\"5.15.4\\""', ['FA "5.15.4"']),
        ("'it\\'s' + \"\"", ["it's"]),
        ('"\\x41\\u0042\\u{43}\\n\\q"', ["ABC\nq"]),
        ("sem aspas 22.2.2", []),
    ],
)
def test_r21_5_le_o_valor_das_strings_do_trecho(trecho: str, esperado: list[str]) -> None:
    assert strings_do_trecho(trecho) == esperado


def test_r21_5_formas_escritas_cobrem_as_tres_aspas_com_escape() -> None:
    assert formas_escritas('FA "5.15.4"') == [
        '"FA \\"5.15.4\\""',
        "'FA \"5.15.4\"'",
        '`FA "5.15.4"`',
    ]


def test_r21_5_formas_escritas_escapam_quebra_de_linha_e_barra() -> None:
    assert formas_escritas("a\\b\nc")[0] == '"a\\\\b\\nc"'


def test_r21_5_escape_unicode_fora_do_intervalo_vira_caractere_de_substituicao() -> None:
    assert strings_do_trecho('"a\\u{110000}b\\u{FFFFFFFFFFFFFFFFFFFF}"') == ["a\ufffdb\ufffd"]


def test_r21_5_aspa_seguida_de_muitas_barras_sem_fechar_nao_trava_a_leitura() -> None:
    inicio = time.monotonic()

    assert strings_do_trecho('"' + "\\" * 60) == []
    assert time.monotonic() - inicio < 1
