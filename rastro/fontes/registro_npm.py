import json
from typing import Protocol
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.pacote_npm import (
    LIMITE_DO_PACOTE_EM_MEGABYTES,
    MEGABYTE,
    NOME_DO_REGISTRO,
    conferir_integridade,
    ler_arquivos_de_codigo,
)
from rastro.fontes.requisicao_http import (
    ERROS_DE_CONEXAO,
    TEMPO_LIMITE_EM_SEGUNDOS,
    motivo_da_falha_de_conexao,
    motivo_do_erro_http,
)

ENDERECO_DO_REGISTRO = "https://registry.npmjs.org"
STATUS_HTTP_PUBLICADO = 200
HTTP_NAO_PUBLICADO = 404


class RegistroDePacotes(Protocol):
    def existe(self, pacote: str, versao: str) -> bool: ...

    def ler_codigo(self, pacote: str, versao: str) -> list[str]: ...


class RegistroNpm:
    def existe(self, pacote: str, versao: str) -> bool:
        requisicao = montar_requisicao(pacote, versao)
        try:
            with urlopen(requisicao, timeout=TEMPO_LIMITE_EM_SEGUNDOS) as resposta:
                return publicado_pelo_codigo(resposta.status)
        except HTTPError as erro:
            return publicado_pelo_codigo(erro.code)
        except ERROS_DE_CONEXAO as erro:
            raise ConsultaNaoRealizada(motivo_da_falha_de_conexao(NOME_DO_REGISTRO, erro)) from erro

    def ler_codigo(self, pacote: str, versao: str) -> list[str]:
        metadados = baixar(montar_requisicao(pacote, versao))
        endereco_do_pacote, integridade = ler_endereco_e_integridade(metadados)
        dados = baixar(Request(endereco_do_pacote, method="GET"))
        conferir_integridade(dados, integridade)
        return ler_arquivos_de_codigo(dados)


def montar_requisicao(pacote: str, versao: str) -> Request:
    endereco = f"{ENDERECO_DO_REGISTRO}/{quote(pacote, safe='@')}/{quote(versao, safe='')}"
    return Request(endereco, headers={"Accept": "application/json"}, method="GET")


def baixar(requisicao: Request) -> bytes:
    limite = LIMITE_DO_PACOTE_EM_MEGABYTES * MEGABYTE
    try:
        with urlopen(requisicao, timeout=TEMPO_LIMITE_EM_SEGUNDOS) as resposta:
            if resposta.status != STATUS_HTTP_PUBLICADO:
                raise ConsultaNaoRealizada(motivo_do_erro_do_registro(resposta.status))
            dados: bytes = resposta.read(limite + 1)
    except HTTPError as erro:
        raise ConsultaNaoRealizada(motivo_do_erro_do_registro(erro.code)) from erro
    except ERROS_DE_CONEXAO as erro:
        raise ConsultaNaoRealizada(motivo_da_falha_de_conexao(NOME_DO_REGISTRO, erro)) from erro
    if len(dados) > limite:
        raise ConsultaNaoRealizada(f"pacote acima de {LIMITE_DO_PACOTE_EM_MEGABYTES} MB")
    return dados


def ler_endereco_e_integridade(metadados: bytes) -> tuple[str, str]:
    try:
        distribuicao = json.loads(metadados)["dist"]
        endereco, integridade = distribuicao["tarball"], distribuicao["integrity"]
    except (ValueError, TypeError, KeyError) as erro:
        raise ConsultaNaoRealizada(motivo_fora_do_formato()) from erro
    if not isinstance(endereco, str) or not isinstance(integridade, str):
        raise ConsultaNaoRealizada(motivo_fora_do_formato())
    if not endereco.startswith(f"{ENDERECO_DO_REGISTRO}/"):
        raise ConsultaNaoRealizada(f"pacote fora do {NOME_DO_REGISTRO}: {endereco}")
    return endereco, integridade


def publicado_pelo_codigo(codigo: int) -> bool:
    if codigo == STATUS_HTTP_PUBLICADO:
        return True
    if codigo == HTTP_NAO_PUBLICADO:
        return False
    raise ConsultaNaoRealizada(motivo_do_erro_do_registro(codigo))


def motivo_fora_do_formato() -> str:
    return f"resposta do {NOME_DO_REGISTRO} fora do formato esperado"


def motivo_do_erro_do_registro(codigo: int) -> str:
    recusa = f"resposta inesperada do {NOME_DO_REGISTRO}"
    return motivo_do_erro_http(NOME_DO_REGISTRO, codigo, motivo_da_recusa=recusa)
