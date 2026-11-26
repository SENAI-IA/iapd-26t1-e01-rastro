import pytest

from rastro.fontes.faixas_do_osv import FaixaSemver, faixas_dos_eventos_semver


@pytest.mark.parametrize(
    ("eventos", "esperado"),
    [
        (
            [{"introduced": "1.2.0"}, {"fixed": "3.5.0"}],
            [FaixaSemver(">= 1.2.0, < 3.5.0", "3.5.0")],
        ),
        ([{"introduced": "0"}, {"fixed": "3.5.0"}], [FaixaSemver("< 3.5.0", "3.5.0")]),
        (
            [{"introduced": "1.0.0"}, {"last_affected": "1.0.5"}],
            [FaixaSemver(">= 1.0.0, <= 1.0.5", None)],
        ),
        ([{"introduced": "0"}, {"last_affected": "1.0.5"}], [FaixaSemver("<= 1.0.5", None)]),
        ([{"introduced": "2.0.0"}], [FaixaSemver(">= 2.0.0", None)]),
        ([{"introduced": "0"}], [FaixaSemver(">= 0", None)]),
        ([{"fixed": "1.0.0"}], []),
        ([{"introduced": "1.0.0"}, {"limit": "2.0.0"}], [FaixaSemver(">= 1.0.0", None)]),
        (
            [{"introduced": "0"}, {"fixed": "1.0.0"}, {"introduced": "2.0.0"}, {"fixed": "2.1.0"}],
            [FaixaSemver("< 1.0.0", "1.0.0"), FaixaSemver(">= 2.0.0, < 2.1.0", "2.1.0")],
        ),
    ],
)
def test_r04a_1_le_os_eventos_semver_como_faixa_de_versao(
    eventos: list[dict[str, str]], esperado: list[FaixaSemver]
) -> None:
    assert faixas_dos_eventos_semver(eventos) == esperado
