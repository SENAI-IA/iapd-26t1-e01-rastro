import time
from dataclasses import dataclass

from rastro.ia.provedor import FalhaDoProvedor, ProvedorDeIA
from rastro.ia.sanitizacao import sanitizar


@dataclass(frozen=True)
class ChamadaDaIA:
    etapa: str
    provedor: str
    entrada: str
    resposta: str
    duracao_s: float
    tokens: int | None
    sucesso: bool


class ClienteDeIA:
    def __init__(self, provedor: ProvedorDeIA) -> None:
        self.provedor = provedor
        self.chamadas: list[ChamadaDaIA] = []

    def perguntar(self, etapa: str, prompt: str) -> str | None:
        entrada = sanitizar(prompt)
        inicio = time.perf_counter()
        try:
            resposta = self.provedor.executar(entrada)
        except FalhaDoProvedor as falha:
            self.registrar(
                etapa=etapa,
                entrada=entrada,
                resposta=falha.motivo,
                duracao_em_segundos=segundos_desde(inicio),
                tokens=None,
                sucesso=False,
            )
            return None
        duracao_em_segundos = segundos_desde(inicio)
        self.registrar(
            etapa=etapa,
            entrada=entrada,
            resposta=sanitizar(resposta.texto),
            duracao_em_segundos=duracao_em_segundos,
            tokens=resposta.tokens,
            sucesso=True,
        )
        return resposta.texto

    def registrar(
        self,
        etapa: str,
        entrada: str,
        resposta: str,
        duracao_em_segundos: float,
        tokens: int | None,
        sucesso: bool,
    ) -> None:
        chamada = ChamadaDaIA(
            etapa, self.provedor.nome, entrada, resposta, duracao_em_segundos, tokens, sucesso
        )
        self.chamadas.append(chamada)


def segundos_desde(inicio: float) -> float:
    return round(time.perf_counter() - inicio, 1)
