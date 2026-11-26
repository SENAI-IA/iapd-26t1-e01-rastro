import json
from typing import Any

from rastro.ia.provedor import FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores.contagem_de_tokens import somar_tokens
from rastro.ia.provedores.execucao_da_cli import executar_cli_da_ia

OPCOES_SEM_GRAVACAO = [
    "exec",
    "--skip-git-repo-check",
    "--sandbox",
    "read-only",
    "--disable",
    "shell_tool",
    "--disable",
    "unified_exec",
    "--ephemeral",
    "--json",
    "-",
]
CAMPOS_DE_TOKENS = ("input_tokens", "output_tokens")


class ProvedorCodex:
    nome = "codex"

    def __init__(self, executavel: str) -> None:
        self.executavel = executavel

    def executar(self, prompt: str) -> RespostaDoProvedor:
        saida_da_cli = executar_cli_da_ia(self.executavel, OPCOES_SEM_GRAVACAO, prompt, "Codex")
        return ler_resposta(saida_da_cli)


def ler_resposta(saida_da_cli: str) -> RespostaDoProvedor:
    eventos = ler_eventos(saida_da_cli)
    texto = ultima_mensagem_do_agente(eventos)
    if texto is None:
        raise FalhaDoProvedor("a CLI do Codex respondeu sem agent_message")
    return RespostaDoProvedor(texto, somar_tokens(uso_do_turno(eventos), CAMPOS_DE_TOKENS))


def ler_eventos(saida_da_cli: str) -> list[dict[str, Any]]:
    eventos = []
    for linha in saida_da_cli.splitlines():
        evento = ler_linha(linha)
        if evento is not None:
            eventos.append(evento)
    return eventos


def ler_linha(linha: str) -> dict[str, Any] | None:
    try:
        evento = json.loads(linha)
    except json.JSONDecodeError:
        return None
    return evento if isinstance(evento, dict) else None


def ultima_mensagem_do_agente(eventos: list[dict[str, Any]]) -> str | None:
    ultima_mensagem = None
    for evento in eventos:
        texto = texto_do_agente(evento)
        if texto is not None:
            ultima_mensagem = texto
    return ultima_mensagem


def texto_do_agente(evento: dict[str, Any]) -> str | None:
    if not evento_e_mensagem_do_agente(evento):
        return None
    texto = evento["item"].get("text")
    return texto if isinstance(texto, str) and texto.strip() else None


def evento_e_mensagem_do_agente(evento: dict[str, Any]) -> bool:
    item = evento.get("item")
    return (
        evento.get("type") == "item.completed"
        and isinstance(item, dict)
        and item.get("type") == "agent_message"
    )


def uso_do_turno(eventos: list[dict[str, Any]]) -> Any:
    turnos = [evento for evento in eventos if evento.get("type") == "turn.completed"]
    return turnos[-1].get("usage") if turnos else None
