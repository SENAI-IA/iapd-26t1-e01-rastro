import json
from collections.abc import Callable
from http.client import HTTPException
from typing import Any, TypeVar
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rastro.fontes.conector import ConsultaNaoRealizada

TEMPO_LIMITE_EM_SEGUNDOS = 15
CODIGOS_DE_LIMITE_DE_CONSULTAS = (403, 429)
ERROS_DE_FORMATO = (KeyError, TypeError, ValueError, AttributeError)
ERROS_DE_CONEXAO = (URLError, TimeoutError, HTTPException, OSError)

Leitura = TypeVar("Leitura")


def baixar_json(
    requisicao: Request,
    nome_da_fonte: str,
    codigos_de_limite: tuple[int, ...] = CODIGOS_DE_LIMITE_DE_CONSULTAS,
) -> Any:
    try:
        with urlopen(requisicao, timeout=TEMPO_LIMITE_EM_SEGUNDOS) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except HTTPError as erro:
        motivo = motivo_do_erro_http(nome_da_fonte, erro.code, codigos_de_limite)
        raise ConsultaNaoRealizada(motivo) from erro
    except (UnicodeDecodeError, json.JSONDecodeError) as erro:
        raise ConsultaNaoRealizada(f"resposta do {nome_da_fonte} não é JSON") from erro
    except ERROS_DE_CONEXAO as erro:
        raise ConsultaNaoRealizada(motivo_da_falha_de_conexao(nome_da_fonte, erro)) from erro


def ler_resposta(leitura: Callable[[], Leitura], nome_da_fonte: str) -> Leitura:
    try:
        return leitura()
    except ERROS_DE_FORMATO as erro:
        raise ConsultaNaoRealizada(f"resposta inesperada do {nome_da_fonte}") from erro


def motivo_da_falha_de_conexao(nome_da_fonte: str, erro: Exception) -> str:
    if isinstance(erro, URLError):
        return motivo_sem_resposta(nome_da_fonte, erro.reason)
    if isinstance(erro, TimeoutError):
        return motivo_sem_resposta(nome_da_fonte, "tempo esgotado")
    return motivo_de_conexao_interrompida(nome_da_fonte, erro)


def motivo_sem_resposta(nome_da_fonte: str, detalhe: object) -> str:
    return f"sem resposta do {nome_da_fonte}: {detalhe}"


def motivo_de_conexao_interrompida(nome_da_fonte: str, erro: Exception) -> str:
    return f"conexão com o {nome_da_fonte} interrompida: {erro}"


def motivo_do_erro_http(
    nome_da_fonte: str,
    codigo: int,
    codigos_de_limite: tuple[int, ...] = CODIGOS_DE_LIMITE_DE_CONSULTAS,
    motivo_da_recusa: str | None = None,
) -> str:
    if codigo in codigos_de_limite:
        return f"limite de consultas do {nome_da_fonte} atingido (HTTP {codigo})"
    if codigo >= 500:
        return f"erro no servidor do {nome_da_fonte} (HTTP {codigo})"
    recusa = motivo_da_recusa or f"o {nome_da_fonte} recusou a consulta"
    return f"{recusa} (HTTP {codigo})"
