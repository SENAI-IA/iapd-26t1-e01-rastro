import shutil
import time
from dataclasses import dataclass
from typing import Protocol

from rastro.ia.sanitizacao import sanitizar

IA_PADRAO = "kiro"
VARIAVEL_DA_IA = "RASTRO_IA"
EXECUTAVEIS_DAS_IAS: dict[str, str] = {
    "kiro": "kiro-cli",
    "claude": "claude",
    "codex": "codex",
}


@dataclass(frozen=True)
class RespostaDoProvedor:
    texto: str
    tokens: int | None


class FalhaDoProvedor(Exception):
    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


class ProvedorDeIA(Protocol):
    nome: str

    def executar(self, prompt: str) -> RespostaDoProvedor: ...


@dataclass(frozen=True)
class ChamadaIA:
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
        self.chamadas: list[ChamadaIA] = []

    def perguntar(self, etapa: str, prompt: str) -> str | None:
        entrada = sanitizar(prompt)
        inicio = time.perf_counter()
        try:
            resposta = self.provedor.executar(entrada)
        except FalhaDoProvedor as falha:
            self.registrar(etapa, entrada, falha.motivo, segundos_desde(inicio), None, False)
            return None
        duracao_s = segundos_desde(inicio)
        resposta_registrada = sanitizar(resposta.texto)
        self.registrar(etapa, entrada, resposta_registrada, duracao_s, resposta.tokens, True)
        return resposta.texto

    def registrar(
        self,
        etapa: str,
        entrada: str,
        resposta: str,
        duracao_s: float,
        tokens: int | None,
        sucesso: bool,
    ) -> None:
        chamada = ChamadaIA(
            etapa, self.provedor.nome, entrada, resposta, duracao_s, tokens, sucesso
        )
        self.chamadas.append(chamada)


def segundos_desde(inicio: float) -> float:
    return round(time.perf_counter() - inicio, 1)


class ErroNaEscolhaDaIa(Exception):
    pass


class IaInvalida(ErroNaEscolhaDaIa):
    def __init__(self, nome: str, origem: str) -> None:
        opcoes = ", ".join(EXECUTAVEIS_DAS_IAS)
        super().__init__(f"IA inválida em {origem}: '{nome}'. Opções válidas: {opcoes}.")


class CliDaIaAusente(ErroNaEscolhaDaIa):
    def __init__(self, nome: str, executavel: str) -> None:
        super().__init__(f"a CLI da IA {nome} ({executavel}) não foi encontrada no sistema")


def escolher_ia(opcao_ia: str | None, variavel_de_ambiente: str | None) -> str:
    if opcao_ia is not None:
        return validar_ia(opcao_ia, "--ia")
    if variavel_de_ambiente:
        return validar_ia(variavel_de_ambiente, VARIAVEL_DA_IA)
    return IA_PADRAO


def validar_ia(nome: str, origem: str) -> str:
    normalizado = nome.strip().lower()
    if normalizado not in EXECUTAVEIS_DAS_IAS:
        raise IaInvalida(nome, origem)
    return normalizado


def localizar_cli(nome_da_ia: str) -> str:
    executavel = EXECUTAVEIS_DAS_IAS[nome_da_ia]
    caminho = shutil.which(executavel)
    if caminho is None:
        raise CliDaIaAusente(nome_da_ia, executavel)
    return caminho
