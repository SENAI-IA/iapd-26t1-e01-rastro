import io
import sys

import pytest

from rastro.terminal.cores import ativar_cores_no_terminal
from rastro.terminal.linha_ao_vivo import LinhaAoVivo


def test_r24_19_no_color_desliga_o_destaque(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")

    assert ativar_cores_no_terminal() is False
    assert LinhaAoVivo(io.StringIO(), ao_vivo=True).cores is False


@pytest.mark.skipif(sys.platform == "win32", reason="no Windows depende do console aberto")
def test_r24_19_sem_no_color_fora_do_windows_as_cores_ficam_ligadas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert ativar_cores_no_terminal() is True
