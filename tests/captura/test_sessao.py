import pytest

from rastro.captura.sessao import FalhaAoNavegar


def test_r24_10_falha_ao_navegar_leva_o_motivo_do_navegador() -> None:
    with pytest.raises(FalhaAoNavegar, match="ERR_CONNECTION_REFUSED"):
        raise FalhaAoNavegar("net::ERR_CONNECTION_REFUSED")
