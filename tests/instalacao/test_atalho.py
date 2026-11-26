import sys
from pathlib import Path

import pytest

from rastro.instalacao.atalho import MARCA, python_do_sistema, texto_do_atalho_windows


def test_r17_3_atalho_do_windows_chama_o_rastro_do_projeto() -> None:
    texto = texto_do_atalho_windows(Path("C:/Python310/python.exe"), Path("C:/rastro"))

    assert MARCA in texto
    assert "PYTHONPATH=" in texto
    assert "-m rastro %* & exit /b" in texto
    assert texto.endswith("\r\n")


def test_r17_3_python_do_atalho_fica_fora_do_venv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "prefix", "/projeto/.venv")
    monkeypatch.setattr(sys, "base_prefix", sys.base_prefix)

    python = python_do_sistema()

    assert ".venv" not in python.parts
