from rastro.terminal.formatacao import cortar_no_limite, destacar, escrever_tempo


def test_r13_10_tempo_em_minutos_e_segundos() -> None:
    assert escrever_tempo(0) == "0:00"
    assert escrever_tempo(65.9) == "1:05"


def test_r13_10_texto_longo_e_cortado_com_reticencias() -> None:
    assert cortar_no_limite("abcdef", 10) == "abcdef"
    assert cortar_no_limite("abcdefghij", 5) == "abcd…"


def test_r24_19_pedido_a_pessoa_sai_destacado_linha_por_linha() -> None:
    assert destacar("feche a janela\nou aperte Ctrl+C") == (
        "\x1b[1;33mfeche a janela\x1b[0m\n\x1b[1;33mou aperte Ctrl+C\x1b[0m"
    )
