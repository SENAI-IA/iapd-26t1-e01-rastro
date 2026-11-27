from typing import Any

from rastro.ia.provedor import FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores.execucao_da_cli import executar_cli_da_ia
from rastro.ia.provedores.linhas_json import ler_eventos

OPCOES_SEM_FERRAMENTAS = [
    "chat",
    "--no-interactive",
    "--trust-tools=",
    "--output-format",
    "stream-json",
]
STATUS_DE_SUCESSO = "success"
UNIDADE_DE_CREDITO = "credit"


class ProvedorKiro:
    nome = "kiro"

    def __init__(self, executavel: str) -> None:
        self.executavel = executavel

    def executar(self, prompt: str) -> RespostaDoProvedor:
        saida_da_cli = executar_cli_da_ia(self.executavel, OPCOES_SEM_FERRAMENTAS, prompt, "Kiro")
        return ler_resposta(saida_da_cli)


def ler_resposta(saida_da_cli: str) -> RespostaDoProvedor:
    eventos = ler_eventos(saida_da_cli)
    fim = dados_do_fim(eventos)
    status = fim.get("status")
    if status is not None and status != STATUS_DE_SUCESSO:
        raise FalhaDoProvedor(f"a CLI do Kiro terminou com status {status}")
    texto = texto_final(fim) or texto_dos_pedacos(eventos)
    if not texto.strip():
        raise FalhaDoProvedor("a CLI do Kiro respondeu sem texto")
    return RespostaDoProvedor(texto.strip(), tokens=None, creditos=somar_creditos(eventos))


def dados_do_fim(eventos: list[dict[str, Any]]) -> dict[str, Any]:
    fins = [evento for evento in eventos if evento.get("type") == "runFinished"]
    if not fins:
        return {}
    dados = fins[-1].get("data")
    return dados if isinstance(dados, dict) else {}


def texto_final(fim: dict[str, Any]) -> str:
    texto = fim.get("finalText")
    if not isinstance(texto, str) or fim.get("finalTextTruncated") is True:
        return ""
    return texto


def texto_dos_pedacos(eventos: list[dict[str, Any]]) -> str:
    return "".join(texto_do_pedaco(evento) for evento in eventos)


def texto_do_pedaco(evento: dict[str, Any]) -> str:
    atualizacao = atualizacao_da_sessao(evento)
    if atualizacao.get("sessionUpdate") != "agent_message_chunk":
        return ""
    conteudo = atualizacao.get("content")
    texto = conteudo.get("text") if isinstance(conteudo, dict) else None
    return texto if isinstance(texto, str) else ""


def atualizacao_da_sessao(evento: dict[str, Any]) -> dict[str, Any]:
    dados = evento.get("data")
    if evento.get("type") != "sessionUpdate" or not isinstance(dados, dict):
        return {}
    atualizacao = dados.get("update")
    return atualizacao if isinstance(atualizacao, dict) else {}


def somar_creditos(eventos: list[dict[str, Any]]) -> float | None:
    medicoes = [medicao for evento in eventos for medicao in medicoes_do_evento(evento)]
    creditos = [credito for credito in map(credito_da_medicao, medicoes) if credito is not None]
    if not creditos:
        return None
    return sum(creditos)


def medicoes_do_evento(evento: dict[str, Any]) -> list[Any]:
    dados = evento.get("data")
    if evento.get("type") != "metadata" or not isinstance(dados, dict):
        return []
    medicoes = dados.get("meteringUsage")
    return medicoes if isinstance(medicoes, list) else []


def credito_da_medicao(medicao: Any) -> float | None:
    if not isinstance(medicao, dict) or medicao.get("unit") != UNIDADE_DE_CREDITO:
        return None
    valor = medicao.get("value")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
        return None
    return float(valor)
