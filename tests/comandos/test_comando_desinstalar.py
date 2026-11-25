from pathlib import Path

import pytest

from rastro import atalho
from rastro.atalho import (
    FIM_DO_BLOCO,
    desinstalar_no_unix,
    instalar_no_unix,
    sobras_da_instalacao,
)
from rastro.cli import executar
from tests.test_atalho import ambiente, projeto_do_install_sh, somente_unix


def test_r17_3_cli_desinstalar_sem_nada_instalado_retorna_0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(atalho, "desinstalar", lambda: desinstalar_no_unix(tmp_path))
    monkeypatch.setattr(atalho, "sobras", lambda: [])

    assert executar(["desinstalar"]) == 0
    assert capsys.readouterr().out == "O comando rastro não está instalado.\n"


def test_r17_3_cli_desinstalar_confirma_o_que_removeu(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    instalar_no_unix(tmp_path, ambiente(tmp_path))
    monkeypatch.setattr(atalho, "desinstalar", lambda: desinstalar_no_unix(tmp_path))
    monkeypatch.setattr(atalho, "sobras", lambda: [])

    assert executar(["desinstalar"]) == 0

    assert capsys.readouterr().out == "Comando rastro removido.\n"
    assert FIM_DO_BLOCO not in (tmp_path / ".bashrc").read_text(encoding="utf-8")


@somente_unix
def test_r17_4_cli_desinstalar_mostra_como_limpar_tudo_sem_apagar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    projeto = projeto_do_install_sh(tmp_path)
    (tmp_path / "Rastro").mkdir()
    instalar_no_unix(tmp_path, ambiente(tmp_path))
    monkeypatch.setattr(atalho, "desinstalar", lambda: desinstalar_no_unix(tmp_path))
    monkeypatch.setattr(atalho, "sobras", lambda: sobras_da_instalacao(tmp_path, projeto))

    assert executar(["desinstalar"]) == 0

    assert capsys.readouterr().out == (
        "Comando rastro removido.\n"
        "Para limpar tudo, apague também:\n"
        f"  os arquivos do Rastro: rm -rf {projeto}\n"
        "  suas gravações e relatórios (guarde antes o que quiser manter): "
        f"rm -rf {tmp_path / 'Rastro'}\n"
    )
    assert projeto.is_dir()
    assert (tmp_path / "Rastro").is_dir()
