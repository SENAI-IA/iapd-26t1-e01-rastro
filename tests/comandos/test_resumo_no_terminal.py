from pathlib import Path

import pytest

from rastro.cli import executar
from tests.dubles import DADOS, PASTA_DA_LOJA, analisar_loja


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_8_mostra_a_pasta_o_html_o_json_e_o_resumo_de_uma_linha(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    analisar_loja(tmp_path)

    saida = capsys.readouterr().out
    assert f"Relatório gravado em: {tmp_path / PASTA_DA_LOJA}" in saida
    assert f"HTML: {tmp_path / PASTA_DA_LOJA / 'relatorio.html'}" in saida
    assert f"JSON: {tmp_path / PASTA_DA_LOJA / 'relatorio.json'}" in saida
    assert (
        "Resumo: loja.exemplo.com · bibliotecas: 2 (1 com falhas) · achados: 2"
        " · nota máxima: 8,3 · ações: 7 (1 alta, 3 média, 3 baixa, 0 a avaliar)"
    ) in saida


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_8_resumo_sem_achados_fala_sem_nota(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    har = DADOS / "har-sem-text.har"
    executar(["analisar", str(har), "--sem-ia", "--saida", str(tmp_path)])

    assert "nota máxima: sem nota" in capsys.readouterr().out
