import subprocess
import sys

import pytest

from rastro.cli import executar


def test_ajuda_abre_e_retorna_0(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as saida:
        executar(["--help"])

    assert saida.value.code == 0
    assert "usage: rastro" in capsys.readouterr().out


def test_sem_argumentos_mostra_a_ajuda_e_retorna_0(capsys: pytest.CaptureFixture[str]) -> None:
    assert executar([]) == 0
    assert "HAR" in capsys.readouterr().out


def test_python_m_rastro_help_retorna_0() -> None:
    resultado = subprocess.run(
        [sys.executable, "-m", "rastro", "--help"],
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert resultado.returncode == 0
    assert "usage: rastro" in resultado.stdout
