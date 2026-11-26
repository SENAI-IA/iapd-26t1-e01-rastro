import pytest

from rastro.comandos.saida_de_erro import encerrar_com_erro


def test_r01_2_erro_vai_para_a_saida_de_erro_com_prefixo_e_codigo_1(
    capsys: pytest.CaptureFixture[str],
) -> None:
    codigo = encerrar_com_erro("o arquivo não existe")

    saidas = capsys.readouterr()
    assert codigo == 1
    assert saidas.err == "rastro: erro: o arquivo não existe\n"
    assert saidas.out == ""
