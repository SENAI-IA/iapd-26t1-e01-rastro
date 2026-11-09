import json
import subprocess
from typing import Any, TypeGuard

from rastro.ia.cliente import FalhaDoProvedor, RespostaDoProvedor

OPCOES_SEM_FERRAMENTAS = ["-p", "--output-format", "json", "--tools", ""]
TEMPO_LIMITE_EM_SEGUNDOS = 120
CAMPOS_DE_TOKENS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


class ProvedorClaude:
    nome = "claude"

    def __init__(self, executavel: str) -> None:
        self.executavel = executavel

    def executar(self, prompt: str) -> RespostaDoProvedor:
        saida = self.rodar_cli(prompt)
        return ler_resposta(saida)

    def rodar_cli(self, prompt: str) -> str:
        try:
            processo = subprocess.run(
                [self.executavel, *OPCOES_SEM_FERRAMENTAS],
                input=prompt,
                capture_output=True,
                encoding="utf-8",
                timeout=TEMPO_LIMITE_EM_SEGUNDOS,
            )
        except subprocess.TimeoutExpired as erro:
            raise FalhaDoProvedor(
                f"a CLI do Claude passou do tempo limite de {TEMPO_LIMITE_EM_SEGUNDOS} s"
            ) from erro
        except OSError as erro:
            raise FalhaDoProvedor(f"a CLI do Claude não pôde ser executada: {erro}") from erro
        if processo.returncode != 0:
            raise FalhaDoProvedor(
                f"a CLI do Claude terminou com código de saída {processo.returncode}"
            )
        return processo.stdout


def ler_resposta(saida: str) -> RespostaDoProvedor:
    resposta = ler_json(saida)
    if resposta.get("is_error") is True:
        raise FalhaDoProvedor("a CLI do Claude informou erro na resposta (is_error)")
    texto = resposta.get("result")
    if not isinstance(texto, str) or not texto.strip():
        raise FalhaDoProvedor("a CLI do Claude respondeu sem texto")
    return RespostaDoProvedor(texto, somar_tokens(resposta.get("usage")))


def ler_json(saida: str) -> dict[str, Any]:
    try:
        resposta = json.loads(saida)
    except json.JSONDecodeError as erro:
        raise FalhaDoProvedor("a resposta da CLI do Claude não é JSON") from erro
    if not isinstance(resposta, dict):
        raise FalhaDoProvedor("a resposta da CLI do Claude não é um objeto JSON")
    return resposta


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
