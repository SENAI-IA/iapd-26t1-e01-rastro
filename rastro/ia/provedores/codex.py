import json
import subprocess
from typing import Any, TypeGuard

from rastro.ia.cliente import FalhaDoProvedor, RespostaDoProvedor

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
TEMPO_LIMITE_EM_SEGUNDOS = 120
CAMPOS_DE_TOKENS = ("input_tokens", "output_tokens")


class ProvedorCodex:
    nome = "codex"

    def __init__(self, executavel: str) -> None:
        self.executavel = executavel

    def executar(self, prompt: str) -> RespostaDoProvedor:
        saida = self.rodar_cli(prompt)
        return ler_resposta(saida)

    def rodar_cli(self, prompt: str) -> str:
        try:
            processo = subprocess.run(
                [self.executavel, *OPCOES_SEM_GRAVACAO],
                input=prompt,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=TEMPO_LIMITE_EM_SEGUNDOS,
            )
        except subprocess.TimeoutExpired as erro:
            raise FalhaDoProvedor(
                f"a CLI do Codex passou do tempo limite de {TEMPO_LIMITE_EM_SEGUNDOS} s"
            ) from erro
        except OSError as erro:
            raise FalhaDoProvedor(f"a CLI do Codex não pôde ser executada: {erro}") from erro
        if processo.returncode != 0:
            raise FalhaDoProvedor(
                f"a CLI do Codex terminou com código de saída {processo.returncode}"
            )
        return processo.stdout


def ler_resposta(saida: str) -> RespostaDoProvedor:
    eventos = ler_eventos(saida)
    texto = ultima_mensagem_do_agente(eventos)
    if texto is None:
        raise FalhaDoProvedor("a CLI do Codex respondeu sem agent_message")
    return RespostaDoProvedor(texto, somar_tokens(uso_do_turno(eventos)))


def ler_eventos(saida: str) -> list[dict[str, Any]]:
    eventos = []
    for linha in saida.splitlines():
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
    textos = [texto for evento in eventos if (texto := texto_do_agente(evento)) is not None]
    return textos[-1] if textos else None


def texto_do_agente(evento: dict[str, Any]) -> str | None:
    if not e_mensagem_do_agente(evento):
        return None
    texto = evento["item"].get("text")
    return texto if isinstance(texto, str) and texto.strip() else None


def e_mensagem_do_agente(evento: dict[str, Any]) -> bool:
    item = evento.get("item")
    return (
        evento.get("type") == "item.completed"
        and isinstance(item, dict)
        and item.get("type") == "agent_message"
    )


def uso_do_turno(eventos: list[dict[str, Any]]) -> Any:
    turnos = [evento for evento in eventos if evento.get("type") == "turn.completed"]
    return turnos[-1].get("usage") if turnos else None


def somar_tokens(uso: Any) -> int | None:
    if not isinstance(uso, dict):
        return None
    total = 0
    for campo in CAMPOS_DE_TOKENS:
        contagem = uso.get(campo)
        if not contagem_valida(contagem):
            return None
        total += contagem
    return total


def contagem_valida(contagem: Any) -> TypeGuard[int]:
    return isinstance(contagem, int) and not isinstance(contagem, bool) and contagem >= 0
