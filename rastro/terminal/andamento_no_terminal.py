import time
from collections.abc import Callable

from rastro.terminal.formatacao import escrever_tempo
from rastro.terminal.linha_ao_vivo import LinhaAoVivo

TEXTO_DA_ETAPA = "[{numero}/{total}] {nome}"
TEXTO_DOS_ITENS = "{feitos} de {total}"
TEXTO_ETAPA_FEITA = "ok"


class AndamentoNoTerminal:
    def __init__(self, linha: LinhaAoVivo, relogio: Callable[[], float] = time.monotonic) -> None:
        self.linha = linha
        self.relogio = relogio
        self.total_de_etapas = 0
        self.numero_da_etapa = 0
        self.nome_da_etapa: str | None = None
        self.inicio = 0.0
        self.total_de_itens = 0
        self.itens_feitos = 0

    def comecar_analise(self, etapas: int) -> None:
        self.total_de_etapas = etapas

    def iniciar_etapa(self, nome: str) -> None:
        self.terminar()
        self.numero_da_etapa += 1
        self.nome_da_etapa = nome
        self.inicio = self.relogio()
        self.total_de_itens = 0
        self.itens_feitos = 0
        if self.linha.ao_vivo:
            self.linha.acompanhar(self.texto)
        else:
            self.linha.imprimir(self.titulo())

    def definir_total_de_itens(self, total: int) -> None:
        self.total_de_itens = total

    def avancar_item(self) -> None:
        self.itens_feitos += 1

    def terminar(self) -> None:
        if self.nome_da_etapa is None:
            return
        if self.linha.ao_vivo:
            self.linha.soltar()
            self.linha.imprimir(f"{self.texto()} · {TEXTO_ETAPA_FEITA}")
        self.nome_da_etapa = None

    def titulo(self) -> str:
        return TEXTO_DA_ETAPA.format(
            numero=self.numero_da_etapa, total=self.total_de_etapas, nome=self.nome_da_etapa
        )

    def texto(self) -> str:
        partes = [self.titulo()]
        if self.total_de_itens:
            feitos = min(self.itens_feitos, self.total_de_itens)
            partes.append(TEXTO_DOS_ITENS.format(feitos=feitos, total=self.total_de_itens))
        partes.append(escrever_tempo(self.relogio() - self.inicio))
        return " · ".join(partes)
