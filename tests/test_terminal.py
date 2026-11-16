import io

import pytest

from rastro.terminal import (
    AndamentoNoTerminal,
    LinhaAoVivo,
    cortar,
    destacar,
    escrever_tempo,
    ligar_cores,
)


class RelogioFalso:
    def __init__(self) -> None:
        self.agora = 0.0

    def __call__(self) -> float:
        return self.agora


def ultima_tela(saida: io.StringIO) -> str:
    return saida.getvalue().split("\r")[-1].rstrip()


def test_r13_10_tempo_em_minutos_e_segundos() -> None:
    assert escrever_tempo(0) == "0:00"
    assert escrever_tempo(65.9) == "1:05"


def test_r13_10_texto_longo_e_cortado_com_reticencias() -> None:
    assert cortar("abcdef", 10) == "abcdef"
    assert cortar("abcdefghij", 5) == "abcd…"


def test_r13_10_fora_do_terminal_mostra_so_o_nome_de_cada_etapa() -> None:
    saida = io.StringIO()
    andamento = AndamentoNoTerminal(LinhaAoVivo(saida, ao_vivo=False))

    andamento.comecar(5)
    andamento.etapa("Lendo o HAR")
    andamento.etapa("Consultando falhas conhecidas")
    andamento.itens(3)
    andamento.avancar()
    andamento.terminar()

    assert saida.getvalue().splitlines() == [
        "[1/5] Lendo o HAR",
        "[2/5] Consultando falhas conhecidas",
    ]


def test_r13_10_no_terminal_mostra_etapa_itens_e_tempo_ao_vivo() -> None:
    saida = io.StringIO()
    relogio = RelogioFalso()
    linha = LinhaAoVivo(saida, ao_vivo=True, largura=lambda: 80)
    andamento = AndamentoNoTerminal(linha, relogio)

    andamento.comecar(7)
    andamento.etapa("Procurando bibliotecas nos bundles com a IA")
    andamento.itens(5)
    andamento.avancar()
    andamento.avancar()
    relogio.agora = 42
    linha.acompanhar(andamento.texto)

    assert ultima_tela(saida) == (
        "[1/7] Procurando bibliotecas nos bundles com a IA · 2 de 5 · 0:42 |"
    )


def test_r13_10_etapa_concluida_fica_no_terminal_com_ok() -> None:
    saida = io.StringIO()
    relogio = RelogioFalso()
    andamento = AndamentoNoTerminal(LinhaAoVivo(saida, ao_vivo=True), relogio)

    andamento.comecar(5)
    andamento.etapa("Lendo o HAR")
    relogio.agora = 3
    andamento.etapa("Reconhecendo as bibliotecas pelos arquivos")
    andamento.terminar()

    linhas = [trecho.strip() for trecho in saida.getvalue().split("\r")]
    assert "[1/5] Lendo o HAR · 0:03 · ok" in "\n".join(linhas)
    assert "[2/5] Reconhecendo as bibliotecas pelos arquivos · 0:00 · ok" in "\n".join(linhas)
    assert saida.getvalue().endswith("\n")


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

    assert saida.getvalue() == "\rGravando |\r          \rpágina 1\n\rGravando |"


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


def test_r24_19_pedido_a_pessoa_sai_destacado_linha_por_linha() -> None:
    assert destacar("feche a janela\nou aperte Ctrl+C") == (
        "\x1b[1;33mfeche a janela\x1b[0m\n\x1b[1;33mou aperte Ctrl+C\x1b[0m"
    )


def test_r24_19_no_terminal_com_cores_o_pedido_sai_destacado() -> None:
    saida = io.StringIO()
    linha = LinhaAoVivo(saida, ao_vivo=True, cores=True)

    linha.pedir("Aperte Enter aqui.")

    assert saida.getvalue() == "\x1b[1;33mAperte Enter aqui.\x1b[0m\n"


def test_r24_19_fora_do_terminal_o_pedido_sai_sem_codigos() -> None:
    saida = io.StringIO()

    LinhaAoVivo(saida, ao_vivo=False).pedir("Aperte Enter aqui.")

    assert saida.getvalue() == "Aperte Enter aqui.\n"


def test_r24_19_no_color_desliga_o_destaque(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")

    assert ligar_cores() is False
    assert LinhaAoVivo(io.StringIO(), ao_vivo=True).cores is False
