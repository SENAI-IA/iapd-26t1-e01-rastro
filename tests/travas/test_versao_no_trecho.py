import pytest

from rastro.travas.versao_no_trecho import versao_esta_no_trecho

TRECHO_DO_ANGULAR = "[`ng-version`,`22.2.2`]"


@pytest.mark.parametrize(
    ("versao", "trecho", "esperado"),
    [
        ("22.2.2", TRECHO_DO_ANGULAR, True),
        ("5.15.4", '`FA "5.15.4"`', True),
        ("3.4.1", "/*! jQuery v3.4.1 | (c) JS Foundation", True),
        ("1.0.0-rc.1", '"1.0.0-rc.1"', True),
        ("2.2.2", TRECHO_DO_ANGULAR, False),
        ("22.2", TRECHO_DO_ANGULAR, False),
        ("3.4.1", '"13.4.1"', False),
        ("3.4.1", '"3.4.10"', False),
        ("3.4.1", '"3.4.1.2"', False),
        ("1.0.0", '"1.0.0-rc.1"', False),
        ("3.4.1", "jquery 3-4-1", False),
    ],
)
def test_r21_3_versao_precisa_aparecer_inteira_no_trecho(
    versao: str, trecho: str, esperado: bool
) -> None:
    assert versao_esta_no_trecho(versao, trecho) is esperado
