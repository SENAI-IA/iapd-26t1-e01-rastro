import os
from pathlib import Path

import pytest

from rastro.cli import executar
from rastro.instalacao import instalador
from rastro.instalacao.instalador import instalar_no_unix
from tests.instalacao.apoio import PATH_SEM_A_PASTA, ambiente, atalho_unix


def test_r17_3_cli_instalar_pede_terminal_novo_quando_mexe_no_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        instalador, "instalar", lambda: instalar_no_unix(tmp_path, ambiente(tmp_path))
    )

    assert executar(["instalar"]) == 0

    assert capsys.readouterr().out == (
        "Pronto! Comando rastro instalado.\nAbra um terminal novo e teste com: rastro --help\n"
    )


def test_r17_3_cli_instalar_com_a_pasta_no_path_testa_no_mesmo_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    path = f"{tmp_path / '.local' / 'bin'}{os.pathsep}{PATH_SEM_A_PASTA}"
    monkeypatch.setattr(
        instalador, "instalar", lambda: instalar_no_unix(tmp_path, ambiente(tmp_path, path=path))
    )

    assert executar(["instalar"]) == 0

    assert capsys.readouterr().out == (
        "Pronto! Comando rastro instalado.\nTeste com: rastro --help\n"
    )


def test_r17_3_cli_instalar_com_comando_de_outro_sai_com_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    outro = atalho_unix(tmp_path)
    outro.parent.mkdir(parents=True)
    outro.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(
        instalador, "instalar", lambda: instalar_no_unix(tmp_path, ambiente(tmp_path))
    )

    assert executar(["instalar"]) == 1
    assert "rastro: erro:" in capsys.readouterr().err
