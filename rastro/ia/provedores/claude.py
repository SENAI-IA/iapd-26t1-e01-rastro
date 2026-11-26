import json
from typing import Any

from rastro.ia.provedor import FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores.contagem_de_tokens import somar_tokens
from rastro.ia.provedores.execucao_da_cli import executar_cli_da_ia

OPCOES_SEM_FERRAMENTAS = ["-p", "--output-format", "json", "--tools", ""]
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
        saida_da_cli = executar_cli_da_ia(self.executavel, OPCOES_SEM_FERRAMENTAS, prompt, "Claude")
        return ler_resposta(saida_da_cli)


def ler_resposta(saida_da_cli: str) -> RespostaDoProvedor:
    resposta = ler_json(saida_da_cli)
    if resposta.get("is_error") is True:
        raise FalhaDoProvedor("a CLI do Claude informou erro na resposta (is_error)")
    texto = resposta.get("result")
    if not isinstance(texto, str) or not texto.strip():
        raise FalhaDoProvedor("a CLI do Claude respondeu sem texto")
    return RespostaDoProvedor(texto, somar_tokens(resposta.get("usage"), CAMPOS_DE_TOKENS))


def ler_json(saida_da_cli: str) -> dict[str, Any]:
    try:
        resposta = json.loads(saida_da_cli)
    except json.JSONDecodeError as erro:
        raise FalhaDoProvedor("a resposta da CLI do Claude não é JSON") from erro
    if not isinstance(resposta, dict):
        raise FalhaDoProvedor("a resposta da CLI do Claude não é um objeto JSON")
    return resposta
