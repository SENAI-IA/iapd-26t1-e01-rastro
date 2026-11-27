import io

from rastro.terminal.andamento_no_terminal import AndamentoNoTerminal
from rastro.terminal.linha_ao_vivo import LinhaAoVivo
from tests.terminal.apoio import ultima_tela


class RelogioFalso:
    def __init__(self) -> None:
        self.agora = 0.0

    def __call__(self) -> float:
        return self.agora


def test_r13_10_fora_do_terminal_mostra_so_o_nome_de_cada_etapa() -> None:
    saida = io.StringIO()
    andamento = AndamentoNoTerminal(LinhaAoVivo(saida, ao_vivo=False))

    andamento.comecar_analise(5)
    andamento.iniciar_etapa("Lendo o HAR")
    andamento.iniciar_etapa("Consultando falhas conhecidas")
    andamento.definir_total_de_itens(3)
    andamento.avancar_item()
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

    andamento.comecar_analise(7)
    andamento.iniciar_etapa("Procurando bibliotecas nos bundles com a IA")
    andamento.definir_total_de_itens(5)
    andamento.avancar_item()
    andamento.avancar_item()
    relogio.agora = 42
    linha.acompanhar(andamento.texto)

    assert ultima_tela(saida) == (
        "⠋ [1/7] Procurando bibliotecas nos bundles com a IA · 2 de 5 · 0:42"
    )


def test_r13_10_etapa_concluida_fica_no_terminal_marcada_como_feita() -> None:
    saida = io.StringIO()
    relogio = RelogioFalso()
    andamento = AndamentoNoTerminal(LinhaAoVivo(saida, ao_vivo=True), relogio)

    andamento.comecar_analise(5)
    andamento.iniciar_etapa("Lendo o HAR")
    relogio.agora = 3
    andamento.iniciar_etapa("Reconhecendo as bibliotecas pelos arquivos")
    andamento.terminar()

    linhas = [trecho.strip() for trecho in saida.getvalue().split("\r")]
    assert "✓ [1/5] Lendo o HAR · 0:03" in "\n".join(linhas)
    assert "✓ [2/5] Reconhecendo as bibliotecas pelos arquivos · 0:00" in "\n".join(linhas)
    assert saida.getvalue().endswith("\n")
