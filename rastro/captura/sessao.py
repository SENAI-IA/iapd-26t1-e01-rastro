from typing import Protocol

FATIA_DE_ESPERA_EM_SEGUNDOS = 0.25


class FalhaAoNavegar(Exception):
    pass


class SessaoDeGravacao(Protocol):
    """O navegador aberto para o auditor, gravando tudo o que recebe num HAR."""

    requisicoes: int
    scripts: int

    def ir(self, url: str) -> None: ...

    def links(self) -> list[str]: ...

    def aberta(self) -> bool: ...

    def esperar(self, segundos: float) -> None: ...


class PedidoDeParada:
    def __init__(self) -> None:
        self.motivo: str | None = None

    def pedir(self, motivo: str) -> None:
        if self.motivo is None:
            self.motivo = motivo


def esperar_a_janela_fechar(sessao: SessaoDeGravacao, parada: PedidoDeParada) -> None:
    while sessao.aberta() and parada.motivo is None:
        sessao.esperar(FATIA_DE_ESPERA_EM_SEGUNDOS)
