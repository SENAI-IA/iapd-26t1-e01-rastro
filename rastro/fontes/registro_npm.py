import base64
import hashlib
import io
import json
import tarfile
from http.client import HTTPException
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
MEGABYTE = 1024 * 1024
LIMITE_DO_PACOTE_EM_MB = 10
LIMITE_DO_CODIGO_DESEMPACOTADO_EM_MB = 50
EXTENSOES_DE_CODIGO = (".js", ".mjs", ".cjs")
PREFIXO_DO_SHA512 = "sha512-"


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
        except URLError as erro:
            raise ConsultaNaoRealizada(motivo_sem_resposta(str(erro.reason))) from erro
        except TimeoutError as erro:
            raise ConsultaNaoRealizada(motivo_sem_resposta("tempo esgotado")) from erro
        except (HTTPException, OSError) as erro:
            raise ConsultaNaoRealizada(motivo_de_conexao_interrompida(erro)) from erro

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
    limite = LIMITE_DO_PACOTE_EM_MB * MEGABYTE
    try:
        with urlopen(requisicao, timeout=TEMPO_LIMITE_EM_SEGUNDOS) as resposta:
            if resposta.status != HTTP_PUBLICADO:
                raise ConsultaNaoRealizada(motivo_do_erro_http(resposta.status))
            dados: bytes = resposta.read(limite + 1)
    except HTTPError as erro:
        raise ConsultaNaoRealizada(motivo_do_erro_http(erro.code)) from erro
    except URLError as erro:
        raise ConsultaNaoRealizada(motivo_sem_resposta(str(erro.reason))) from erro
    except TimeoutError as erro:
        raise ConsultaNaoRealizada(motivo_sem_resposta("tempo esgotado")) from erro
    except (HTTPException, OSError) as erro:
        raise ConsultaNaoRealizada(motivo_de_conexao_interrompida(erro)) from erro
    if len(dados) > limite:
        raise ConsultaNaoRealizada(f"pacote acima de {LIMITE_DO_PACOTE_EM_MB} MB")
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


def conferir_integridade(dados: bytes, integridade: str) -> None:
    esperados = [
        parte.removeprefix(PREFIXO_DO_SHA512)
        for parte in integridade.split()
        if parte.startswith(PREFIXO_DO_SHA512)
    ]
    if not esperados:
        raise ConsultaNaoRealizada(f"pacote sem integridade sha512 no {NOME_DO_REGISTRO}")
    calculado = base64.b64encode(hashlib.sha512(dados).digest()).decode("ascii")
    if calculado not in esperados:
        raise ConsultaNaoRealizada("a integridade do pacote baixado não confere (sha512)")


def ler_arquivos_de_codigo(dados: bytes) -> list[str]:
    try:
        with tarfile.open(fileobj=io.BytesIO(dados), mode="r:gz") as pacote:
            membros = [membro for membro in pacote.getmembers() if e_arquivo_de_codigo(membro)]
            conferir_tamanho_desempacotado(membros)
            return [ler_membro(pacote, membro) for membro in membros]
    except (tarfile.TarError, OSError, EOFError) as erro:
        raise ConsultaNaoRealizada(f"pacote ilegível: {erro}") from erro


def e_arquivo_de_codigo(membro: tarfile.TarInfo) -> bool:
    return membro.isfile() and membro.name.endswith(EXTENSOES_DE_CODIGO)


def conferir_tamanho_desempacotado(membros: list[tarfile.TarInfo]) -> None:
    limite = LIMITE_DO_CODIGO_DESEMPACOTADO_EM_MB * MEGABYTE
    if sum(membro.size for membro in membros) > limite:
        raise ConsultaNaoRealizada(
            f"código do pacote acima de {LIMITE_DO_CODIGO_DESEMPACOTADO_EM_MB} MB desempacotado"
        )


def ler_membro(pacote: tarfile.TarFile, membro: tarfile.TarInfo) -> str:
    arquivo = pacote.extractfile(membro)
    if arquivo is None:
        return ""
    with arquivo:
        return arquivo.read().decode("utf-8", errors="replace")


def publicado_pelo_codigo(codigo: int) -> bool:
    if codigo == HTTP_PUBLICADO:
        return True
    if codigo == HTTP_NAO_PUBLICADO:
        return False
    raise ConsultaNaoRealizada(motivo_do_erro_http(codigo))


def motivo_sem_resposta(detalhe: str) -> str:
    return f"sem resposta do {NOME_DO_REGISTRO}: {detalhe}"


def motivo_de_conexao_interrompida(erro: Exception) -> str:
    return f"conexão com o {NOME_DO_REGISTRO} interrompida: {erro}"


def motivo_fora_do_formato() -> str:
    return f"resposta do {NOME_DO_REGISTRO} fora do formato esperado"


def motivo_do_erro_http(codigo: int) -> str:
    if codigo in (403, 429):
        return f"limite de consultas do {NOME_DO_REGISTRO} atingido (HTTP {codigo})"
    if codigo >= 500:
        return f"erro no servidor do {NOME_DO_REGISTRO} (HTTP {codigo})"
    return f"resposta inesperada do {NOME_DO_REGISTRO} (HTTP {codigo})"
