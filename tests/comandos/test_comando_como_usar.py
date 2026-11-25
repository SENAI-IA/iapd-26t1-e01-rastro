import subprocess
import sys
from pathlib import Path

import pytest

import rastro.comandos.navegador
from rastro.cli import executar
from rastro.relatorio.html import TAG_DOS_DADOS_VAZIA
from tests.dubles import NavegadorFalso


def test_r23_8_como_usar_abre_o_modelo_sem_dados_no_navegador(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    navegador = NavegadorFalso(abre=True)
    monkeypatch.setattr(rastro.comandos.navegador.webbrowser, "open", navegador)

    assert executar(["como-usar"]) == 0

    modelo = Path(rastro.__file__).parent / "relatorio" / "modelo.html"
    assert navegador.enderecos == [modelo.resolve().as_uri()]
    assert TAG_DOS_DADOS_VAZIA in modelo.read_text(encoding="utf-8")
    assert str(modelo.resolve()) in capsys.readouterr().out


def test_r23_8_como_usar_sem_navegador_mostra_o_caminho_e_retorna_0(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(rastro.comandos.navegador.webbrowser, "open", NavegadorFalso(abre=False))

    assert executar(["como-usar"]) == 0

    saida = capsys.readouterr().out
    assert "Não foi possível abrir o navegador" in saida
    assert "modelo.html" in saida


def test_r23_8_como_usar_nao_grava_nada(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rastro.comandos.navegador.webbrowser, "open", NavegadorFalso(abre=True))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.chdir(tmp_path)

    executar(["como-usar"])

    assert list(tmp_path.iterdir()) == []


def test_r23_8_como_usar_nao_deixa_o_navegador_escrever_no_terminal(
    capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def navegador_que_avisa(endereco: str) -> bool:
        subprocess.run(
            [sys.executable, "-c", "import sys; print('aviso'); print('erro', file=sys.stderr)"],
            check=True,
        )
        return True

    monkeypatch.setattr("webbrowser.open", navegador_que_avisa)

    executar(["como-usar"])

    saida = capfd.readouterr()
    assert "aviso" not in saida.out
    assert "erro" not in saida.err
    assert "aberto no navegador" in saida.out
