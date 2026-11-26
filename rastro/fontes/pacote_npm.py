import base64
import hashlib
import io
import tarfile

from rastro.fontes.conector import ConsultaNaoRealizada

NOME_DO_REGISTRO = "registro do npm"
MEGABYTE = 1024 * 1024
LIMITE_DO_PACOTE_EM_MEGABYTES = 10
LIMITE_DO_CODIGO_DESEMPACOTADO_EM_MEGABYTES = 50
LIMITE_DE_ARQUIVOS_NO_PACOTE = 20_000
EXTENSOES_DE_CODIGO = (".js", ".mjs", ".cjs")
PREFIXO_DO_SHA512 = "sha512-"


def conferir_integridade(dados: bytes, integridade: str) -> None:
    esperados = resumos_sha512(integridade)
    if not esperados:
        raise ConsultaNaoRealizada(f"pacote sem integridade sha512 no {NOME_DO_REGISTRO}")
    calculado = base64.b64encode(hashlib.sha512(dados).digest()).decode("ascii")
    if calculado not in esperados:
        raise ConsultaNaoRealizada("a integridade do pacote baixado não confere (sha512)")


def resumos_sha512(integridade: str) -> list[str]:
    resumos = []
    for parte in integridade.split():
        if parte.startswith(PREFIXO_DO_SHA512):
            resumos.append(parte.removeprefix(PREFIXO_DO_SHA512))
    return resumos


def ler_arquivos_de_codigo(dados: bytes) -> list[str]:
    try:
        with tarfile.open(fileobj=io.BytesIO(dados), mode="r:gz") as pacote:
            membros = membros_de_codigo(pacote)
            conferir_tamanho_desempacotado(membros)
            return [ler_membro(pacote, membro) for membro in membros]
    except (tarfile.TarError, OSError, EOFError) as erro:
        raise ConsultaNaoRealizada(f"pacote ilegível: {erro}") from erro


def membros_de_codigo(pacote: tarfile.TarFile) -> list[tarfile.TarInfo]:
    membros = []
    for quantidade, membro in enumerate(pacote, start=1):
        if quantidade > LIMITE_DE_ARQUIVOS_NO_PACOTE:
            raise ConsultaNaoRealizada(
                f"pacote com mais de {LIMITE_DE_ARQUIVOS_NO_PACOTE} arquivos"
            )
        if membro_e_arquivo_de_codigo(membro):
            membros.append(membro)
    return membros


def membro_e_arquivo_de_codigo(membro: tarfile.TarInfo) -> bool:
    return membro.isfile() and membro.name.endswith(EXTENSOES_DE_CODIGO)


def tamanho_somado(membros: list[tarfile.TarInfo]) -> int:
    total = 0
    for membro in membros:
        total += membro.size
    return total


def conferir_tamanho_desempacotado(membros: list[tarfile.TarInfo]) -> None:
    limite = LIMITE_DO_CODIGO_DESEMPACOTADO_EM_MEGABYTES * MEGABYTE
    if tamanho_somado(membros) > limite:
        raise ConsultaNaoRealizada(
            f"código do pacote acima de {LIMITE_DO_CODIGO_DESEMPACOTADO_EM_MEGABYTES} MB "
            "desempacotado"
        )


def ler_membro(pacote: tarfile.TarFile, membro: tarfile.TarInfo) -> str:
    arquivo = pacote.extractfile(membro)
    if arquivo is None:
        return ""
    with arquivo:
        return arquivo.read().decode("utf-8", errors="replace")
