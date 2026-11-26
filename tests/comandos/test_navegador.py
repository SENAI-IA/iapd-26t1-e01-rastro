import subprocess
import sys
from pathlib import Path

import pytest

from rastro.cli import executar
from tests.dubles import HAR_DA_LOJA, PASTA_DA_LOJA, NavegadorFalso, analisar_loja


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_analisar_abre_o_relatorio_html_no_navegador(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, navegador: NavegadorFalso
) -> None:
    assert analisar_loja(tmp_path) == 0

    caminho_do_html = tmp_path / PASTA_DA_LOJA / "relatorio.html"
    assert navegador.enderecos == [caminho_do_html.resolve().as_uri()]
    assert "Relatório aberto no navegador." in capsys.readouterr().out


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_nao_abrir_grava_sem_abrir_o_navegador(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, navegador: NavegadorFalso
) -> None:
    argumentos = ["analisar", str(HAR_DA_LOJA), "--sem-ia", "--saida", str(tmp_path)]

    assert executar([*argumentos, "--nao-abrir"]) == 0

    assert navegador.enderecos == []
    assert (tmp_path / PASTA_DA_LOJA / "relatorio.html").is_file()
    assert "navegador" not in capsys.readouterr().out


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_sem_navegador_avisa_mantem_o_caminho_e_retorna_0(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, navegador: NavegadorFalso
) -> None:
    navegador.abre = False

    assert analisar_loja(tmp_path) == 0

    saida = capsys.readouterr().out
    assert "Não foi possível abrir o navegador" in saida
    assert f"HTML: {tmp_path / PASTA_DA_LOJA / 'relatorio.html'}" in saida


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_analisar_nao_deixa_o_navegador_escrever_no_terminal(
    capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def navegador_que_avisa(endereco: str) -> bool:
        subprocess.run(
            [sys.executable, "-c", "import sys; print('aviso'); print('erro', file=sys.stderr)"],
            check=True,
        )
        return True

    monkeypatch.setattr("webbrowser.open", navegador_que_avisa)

    analisar_loja(tmp_path)

    saida = capfd.readouterr()
    assert "aviso" not in saida.out.splitlines()
    assert "erro" not in saida.err.splitlines()
    assert "Relatório aberto no navegador." in saida.out
