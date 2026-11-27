import io

import pytest

from rastro.terminal import linha_ao_vivo
from rastro.terminal.linha_ao_vivo import LinhaAoVivo
from tests.terminal.apoio import ultima_tela


def test_r13_10_linha_ao_vivo_nao_passa_da_largura_do_terminal() -> None:
    saida = io.StringIO()
    linha = LinhaAoVivo(saida, ao_vivo=True, largura=lambda: 30)

    linha.acompanhar(lambda: "x" * 100)

    assert len(ultima_tela(saida)) < 30


def test_r13_10_imprimir_apaga_a_linha_ao_vivo_e_a_desenha_de_novo() -> None:
    saida = io.StringIO()
    linha = LinhaAoVivo(saida, ao_vivo=True, largura=lambda: 80)
    linha.acompanhar(lambda: "Gravando")

    linha.imprimir("página 1")

    assert saida.getvalue() == "\r⠋ Gravando\r          \rpágina 1\n\r⠋ Gravando"


def test_r13_10_ao_sair_a_linha_ao_vivo_e_apagada() -> None:
    saida = io.StringIO()

    with LinhaAoVivo(saida, ao_vivo=True, largura=lambda: 80) as linha:
        linha.acompanhar(lambda: "Gravando")

    assert ultima_tela(saida) == ""


def test_r13_10_fora_do_terminal_a_linha_ao_vivo_nao_escreve_nada() -> None:
    saida = io.StringIO()

    with LinhaAoVivo(saida, ao_vivo=False) as linha:
        linha.acompanhar(lambda: "Gravando")
        linha.imprimir("página 1")

    assert saida.getvalue() == "página 1\n"


def test_r24_19_no_terminal_com_cores_o_pedido_sai_destacado() -> None:
    saida = io.StringIO()
    linha = LinhaAoVivo(saida, ao_vivo=True, cores=True)

    linha.pedir("Aperte Enter aqui.")

    assert saida.getvalue() == "\x1b[1;33mAperte Enter aqui.\x1b[0m\n"


def test_r24_19_fora_do_terminal_o_pedido_sai_sem_codigos() -> None:
    saida = io.StringIO()

    LinhaAoVivo(saida, ao_vivo=False).pedir("Aperte Enter aqui.")

    assert saida.getvalue() == "Aperte Enter aqui.\n"


def test_r13_10_concluir_marca_a_linha_com_o_sinal_de_feito() -> None:
    saida = io.StringIO()

    LinhaAoVivo(saida, ao_vivo=True).concluir("[1/5] Lendo o HAR · 0:03")

    assert saida.getvalue() == "✓ [1/5] Lendo o HAR · 0:03\n"


def test_r13_10_terminal_sem_unicode_gira_e_conclui_com_ascii() -> None:
    bytes_da_saida = io.BytesIO()
    saida = io.TextIOWrapper(bytes_da_saida, encoding="cp850", newline="")
    linha = LinhaAoVivo(saida, ao_vivo=True, largura=lambda: 80)

    linha.acompanhar(lambda: "Gravando")
    linha.concluir("Gravado")
    saida.flush()

    assert bytes_da_saida.getvalue().decode("cp850").endswith("\rok Gravado\n\r| Gravando")


def test_r13_10_console_antigo_do_windows_gira_com_ascii(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(linha_ao_vivo.sys, "platform", "win32")
    monkeypatch.delenv("WT_SESSION", raising=False)
    saida = io.StringIO()

    LinhaAoVivo(saida, ao_vivo=True, largura=lambda: 80).acompanhar(lambda: "Gravando")

    assert saida.getvalue() == "\r| Gravando"


def test_r13_10_windows_terminal_gira_com_a_cobrinha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(linha_ao_vivo.sys, "platform", "win32")
    monkeypatch.setenv("WT_SESSION", "sessao")
    saida = io.StringIO()

    LinhaAoVivo(saida, ao_vivo=True, largura=lambda: 80).acompanhar(lambda: "Gravando")

    assert saida.getvalue() == "\r⠋ Gravando"
