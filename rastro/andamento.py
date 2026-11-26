from typing import Protocol


class Andamento(Protocol):
    def comecar_analise(self, etapas: int) -> None: ...

    def iniciar_etapa(self, nome: str) -> None: ...

    def definir_total_de_itens(self, total: int) -> None: ...

    def avancar_item(self) -> None: ...


class AndamentoSilencioso:
    def comecar_analise(self, etapas: int) -> None:
        return None

    def iniciar_etapa(self, nome: str) -> None:
        return None

    def definir_total_de_itens(self, total: int) -> None:
        return None

    def avancar_item(self) -> None:
        return None


ANDAMENTO_SILENCIOSO = AndamentoSilencioso()
