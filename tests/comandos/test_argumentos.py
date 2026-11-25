import pytest

from rastro.cli import executar


def test_r14_7_ajuda_abre_e_retorna_0(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as saida:
        executar(["--help"])

    assert saida.value.code == 0
    assert "usage: rastro" in capsys.readouterr().out


def test_r14_7_ajuda_descreve_sem_ia_e_o_que_se_perde_na_mesma_linha(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "200")

    with pytest.raises(SystemExit):
        executar(["analisar", "--help"])

    linhas = capsys.readouterr().out.splitlines()
    linha_da_opcao = next(linha for linha in linhas if linha.strip().startswith("--sem-ia"))
    assert "não procura bibliotecas em bundles e não explica os achados" in linha_da_opcao


def test_r23_8_como_usar_aparece_na_ajuda(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        executar(["--help"])

    assert "como-usar" in capsys.readouterr().out


def test_r24_1_gravar_aparece_na_ajuda(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        executar(["--help"])

    assert "gravar" in capsys.readouterr().out


def test_r17_3_instalar_e_desinstalar_aparecem_na_ajuda(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        executar(["--help"])

    saida = capsys.readouterr().out
    assert "instalar" in saida
    assert "desinstalar" in saida
