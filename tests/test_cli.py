import json
import subprocess
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from rastro import cli
from rastro.cli import AVISO_SEM_IA, executar
from rastro.fluxo import Analise, analisar
from rastro.fontes.conector import ConectorDeAvisos
from rastro.fontes.registro_npm import RegistroDePacotes
from tests.dubles import DADOS, HAR_DA_LOJA, ConectorFalso, RegistroFalso

MOMENTO = datetime(2026, 11, 20, 14, 3, 0)
PASTA_DA_LOJA = Path("loja.exemplo.com") / "2026-11-20_14-03-00"


def analisar_no_momento_fixo(
    caminho_har: Path, fonte: ConectorDeAvisos, registro: RegistroDePacotes
) -> Analise:
    return replace(analisar(caminho_har, fonte, registro), inicio=MOMENTO)


@pytest.fixture
def fontes_falsas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "GitHubAdvisory", ConectorFalso)
    monkeypatch.setattr(cli, "RegistroNpm", RegistroFalso)
    monkeypatch.setattr(cli, "analisar", analisar_no_momento_fixo)


def analisar_loja(saida: Path) -> int:
    return executar(["analisar", str(HAR_DA_LOJA), "--sem-ia", "--saida", str(saida)])


def ler_relatorio(caminho: Path) -> dict[str, Any]:
    with caminho.open(encoding="utf-8") as arquivo:
        dados: dict[str, Any] = json.load(arquivo)
    return dados


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
    assert "analisar" in resultado.stdout


def test_r14_7_ajuda_descreve_sem_ia_e_o_que_se_perde_na_mesma_linha(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "200")

    with pytest.raises(SystemExit):
        executar(["analisar", "--help"])

    linhas = capsys.readouterr().out.splitlines()
    linha_da_opcao = next(linha for linha in linhas if linha.strip().startswith("--sem-ia"))
    assert "não procura bibliotecas em bundles e não explica os achados" in linha_da_opcao


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_1_analisar_sem_ia_grava_o_json_na_pasta_da_analise(tmp_path: Path) -> None:
    assert analisar_loja(tmp_path) == 0

    relatorio = ler_relatorio(tmp_path / PASTA_DA_LOJA / "relatorio.json")
    assert relatorio["versao_formato"] == 1
    assert relatorio["resumo"]
    assert relatorio["analise"]["limitacoes"]


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_2_sem_saida_grava_em_rastro_relatorios_na_pasta_do_usuario(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert executar(["analisar", str(HAR_DA_LOJA), "--sem-ia"]) == 0

    assert (tmp_path / "Rastro" / "relatorios" / PASTA_DA_LOJA / "relatorio.json").is_file()


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_3_har_sem_site_usa_o_nome_do_har(tmp_path: Path) -> None:
    har = DADOS / "har-sem-text.har"
    pasta_esperada = tmp_path / "saida" / "har-sem-text" / "2026-11-20_14-03-00"

    assert executar(["analisar", str(har), "--sem-ia", "--saida", str(tmp_path / "saida")]) == 0

    assert (pasta_esperada / "relatorio.json").is_file()


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_4_pasta_da_analise_existente_encerra_com_1_sem_gravar(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    pasta = tmp_path / PASTA_DA_LOJA
    pasta.mkdir(parents=True)

    assert analisar_loja(tmp_path) == 1

    assert list(pasta.iterdir()) == []
    erro = capsys.readouterr().err
    assert "a pasta da análise já existe" in erro
    assert str(pasta) in erro


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_8_mostra_a_pasta_o_json_e_o_resumo_de_uma_linha(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    analisar_loja(tmp_path)

    saida = capsys.readouterr().out
    assert f"Relatório gravado em: {tmp_path / PASTA_DA_LOJA}" in saida
    assert f"JSON: {tmp_path / PASTA_DA_LOJA / 'relatorio.json'}" in saida
    assert (
        "Resumo: loja.exemplo.com · bibliotecas: 2 (1 com falhas) · achados: 2"
        " · nota máxima: 8,3 · ações: 7 (1 alta, 3 média, 3 baixa, 0 a avaliar)"
    ) in saida


@pytest.mark.usefixtures("fontes_falsas")
def test_r14_5_sem_ia_avisa_no_terminal_no_inicio_e_no_fim(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    analisar_loja(tmp_path)

    linhas = capsys.readouterr().out.splitlines()
    assert linhas[0] == AVISO_SEM_IA
    assert linhas[-1] == AVISO_SEM_IA
    assert any("sem explicação em linguagem simples" in linha for linha in linhas)
    assert any("são os mesmos de uma análise com IA" in linha for linha in linhas)


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_8_resumo_sem_achados_fala_sem_nota(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    har = DADOS / "har-sem-text.har"
    executar(["analisar", str(har), "--sem-ia", "--saida", str(tmp_path)])

    assert "nota máxima: sem nota" in capsys.readouterr().out


def test_analisar_com_ia_ainda_nao_disponivel_encerra_com_1_e_sugere_sem_ia(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    assert executar(["analisar", str(HAR_DA_LOJA), "--saida", str(tmp_path)]) == 1

    assert "--sem-ia" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("fontes_falsas")
def test_r01_2_har_inexistente_encerra_com_1_e_mostra_o_caminho(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    caminho = tmp_path / "nao-existe.har"

    assert executar(["analisar", str(caminho), "--sem-ia", "--saida", str(tmp_path)]) == 1

    assert str(caminho) in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("fontes_falsas")
def test_r01_3_har_invalido_encerra_com_1_sem_relatorio(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    har = DADOS / "har-invalido.har"

    assert executar(["analisar", str(har), "--sem-ia", "--saida", str(tmp_path)]) == 1

    assert "o arquivo não é um HAR válido" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("fontes_falsas")
def test_r17_1_grava_so_o_relatorio_e_nao_altera_o_har(tmp_path: Path) -> None:
    antes = HAR_DA_LOJA.read_bytes()

    analisar_loja(tmp_path)

    arquivos = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert arquivos == [tmp_path / PASTA_DA_LOJA / "relatorio.json"]
    assert HAR_DA_LOJA.read_bytes() == antes
