from rastro.captura.sessao import PedidoDeParada, esperar_a_janela_fechar


class SessaoQueFechaSozinha:
    def __init__(self, fatias_ate_fechar: int) -> None:
        self.requisicoes = 0
        self.scripts = 0
        self.fatias_ate_fechar = fatias_ate_fechar
        self.fatias_esperadas = 0

    def ir(self, url: str) -> None:
        return None

    def links(self) -> list[str]:
        return []

    def aberta(self) -> bool:
        return self.fatias_esperadas < self.fatias_ate_fechar

    def esperar(self, segundos: float) -> None:
        self.fatias_esperadas += 1


def test_r24_7_espera_ate_a_janela_fechar() -> None:
    sessao = SessaoQueFechaSozinha(fatias_ate_fechar=3)

    esperar_a_janela_fechar(sessao, PedidoDeParada())

    assert sessao.fatias_esperadas == 3


def test_r24_7_pedido_de_parada_encerra_a_espera_com_a_janela_aberta() -> None:
    sessao = SessaoQueFechaSozinha(fatias_ate_fechar=100)
    parada = PedidoDeParada()
    parada.pedir("Ctrl+C")

    esperar_a_janela_fechar(sessao, parada)

    assert sessao.fatias_esperadas == 0


def test_r24_7_pedido_de_parada_guarda_o_primeiro_motivo() -> None:
    parada = PedidoDeParada()

    parada.pedir("Ctrl+C")
    parada.pedir("janela fechada")

    assert parada.motivo == "Ctrl+C"
