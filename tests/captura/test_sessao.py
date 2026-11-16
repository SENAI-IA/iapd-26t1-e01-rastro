import threading

from rastro.captura.sessao import PedidoDeParada, esperar_a_janela_fechar, esperar_o_enter


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

    def endereco(self) -> str:
        return "https://loja.exemplo.com/"

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


def test_r24_10_enter_libera_o_robo() -> None:
    sessao = SessaoQueFechaSozinha(fatias_ate_fechar=10_000)

    assert esperar_o_enter(sessao, PedidoDeParada(), lambda: "")


def test_r24_10_sem_terminal_conta_como_enter() -> None:
    def fim_da_entrada() -> str:
        raise EOFError

    sessao = SessaoQueFechaSozinha(fatias_ate_fechar=10_000)

    assert esperar_o_enter(sessao, PedidoDeParada(), fim_da_entrada)


def test_r24_10_janela_fechada_antes_do_enter_nao_libera_o_robo() -> None:
    nunca = threading.Event()
    sessao = SessaoQueFechaSozinha(fatias_ate_fechar=2)

    assert not esperar_o_enter(sessao, PedidoDeParada(), lambda: str(nunca.wait(5)))
    nunca.set()


def test_r24_10_ctrl_c_antes_do_enter_nao_libera_o_robo() -> None:
    nunca = threading.Event()
    parada = PedidoDeParada()
    parada.pedir("Ctrl+C")

    assert not esperar_o_enter(
        SessaoQueFechaSozinha(fatias_ate_fechar=10_000), parada, lambda: str(nunca.wait(5))
    )
    nunca.set()
