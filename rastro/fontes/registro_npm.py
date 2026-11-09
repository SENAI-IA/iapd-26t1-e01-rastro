from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from rastro.fontes.conector import ConsultaNaoRealizada

NOME_DO_REGISTRO = "registro do npm"
ENDERECO_DO_REGISTRO = "https://registry.npmjs.org"
TEMPO_LIMITE_EM_SEGUNDOS = 15
HTTP_PUBLICADO = 200
HTTP_NAO_PUBLICADO = 404


class RegistroDePacotes(Protocol):
    def existe(self, pacote: str, versao: str) -> bool: ...


class RegistroNpm:
    def existe(self, pacote: str, versao: str) -> bool:
        requisicao = montar_requisicao(pacote, versao)
        try:
            with urlopen(requisicao, timeout=TEMPO_LIMITE_EM_SEGUNDOS) as resposta:
                return publicado_pelo_codigo(resposta.status)
        except HTTPError as erro:
            return publicado_pelo_codigo(erro.code)
        except URLError as erro:
            raise ConsultaNaoRealizada(motivo_sem_resposta(str(erro.reason))) from erro
        except TimeoutError as erro:
            raise ConsultaNaoRealizada(motivo_sem_resposta("tempo esgotado")) from erro


def montar_requisicao(pacote: str, versao: str) -> Request:
    endereco = f"{ENDERECO_DO_REGISTRO}/{quote(pacote, safe='@')}/{quote(versao, safe='')}"
    return Request(endereco, headers={"Accept": "application/json"}, method="GET")


def publicado_pelo_codigo(codigo: int) -> bool:
    if codigo == HTTP_PUBLICADO:
        return True
    if codigo == HTTP_NAO_PUBLICADO:
        return False
    raise ConsultaNaoRealizada(motivo_do_erro_http(codigo))


def motivo_sem_resposta(detalhe: str) -> str:
    return f"sem resposta do {NOME_DO_REGISTRO}: {detalhe}"


def motivo_do_erro_http(codigo: int) -> str:
    if codigo in (403, 429):
        return f"limite de consultas do {NOME_DO_REGISTRO} atingido (HTTP {codigo})"
    if codigo >= 500:
        return f"erro no servidor do {NOME_DO_REGISTRO} (HTTP {codigo})"
    return f"resposta inesperada do {NOME_DO_REGISTRO} (HTTP {codigo})"
