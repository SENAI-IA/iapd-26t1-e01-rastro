import subprocess
import sys

import pytest

from rastro import cli
from rastro.cli import executar


def test_r14_7_sem_argumentos_mostra_a_ajuda_e_retorna_0(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert executar([]) == 0
    assert "HAR" in capsys.readouterr().out


def test_r18_1_comando_rastro_sai_com_o_codigo_da_execucao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "executar", lambda: 1)

    with pytest.raises(SystemExit) as saida:
        cli.principal()

    assert saida.value.code == 1


def test_r14_7_python_m_rastro_help_retorna_0() -> None:
    resultado = subprocess.run(
        [sys.executable, "-m", "rastro", "--help"],
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert resultado.returncode == 0
    assert "usage: rastro" in resultado.stdout
    assert "analisar" in resultado.stdout
