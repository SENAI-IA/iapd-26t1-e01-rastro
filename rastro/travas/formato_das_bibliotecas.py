import re
from dataclasses import dataclass

from rastro.travas.json_estrito import (
    TRAVA_FORMATO_FECHADO,
    ForaDoFormato,
    exigir_campos,
    ler_json_sem_texto_fora,
    ler_texto,
)
from rastro.travas.modelos import TravaAcionada

ALVO = "resposta da IA"
CAMPOS_DA_RESPOSTA = {"bibliotecas"}
CAMPOS_DA_BIBLIOTECA = {"pacote", "versao", "trecho"}
TAMANHO_MAXIMO_DO_PACOTE = 214
PADRAO_DO_PACOTE = re.compile(
    r"""
    ^
    (?: @ [a-z0-9~-] [a-z0-9._~-]* / )?
    [a-z0-9~-] [a-z0-9._~-]*
    $
    """,
    re.VERBOSE,
)
PADRAO_DA_VERSAO = re.compile(
    r"""
    ^
    \d+ \. \d+ \. \d+
    (?: - [0-9A-Za-z.-]+ )?
    $
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class BibliotecaSugerida:
    pacote: str
    versao: str
    trecho: str


def conferir_formato(resposta: str) -> tuple[list[BibliotecaSugerida], list[TravaAcionada]]:
    try:
        return ler_bibliotecas_sugeridas(resposta), []
    except ForaDoFormato as erro:
        return [], [TravaAcionada(TRAVA_FORMATO_FECHADO, ALVO, f"resposta descartada: {erro}")]


def ler_bibliotecas_sugeridas(resposta: str) -> list[BibliotecaSugerida]:
    objeto = exigir_campos(ler_json_sem_texto_fora(resposta), CAMPOS_DA_RESPOSTA, "na resposta")
    bibliotecas = objeto["bibliotecas"]
    if not isinstance(bibliotecas, list):
        raise ForaDoFormato("`bibliotecas` não é uma lista")
    return [ler_biblioteca(item) for item in bibliotecas]


def ler_biblioteca(item: object) -> BibliotecaSugerida:
    campos = exigir_campos(item, CAMPOS_DA_BIBLIOTECA, "na biblioteca")
    pacote = ler_texto(campos, "pacote")
    versao = ler_texto(campos, "versao")
    trecho = ler_texto(campos, "trecho")
    if not nome_de_pacote_npm_valido(pacote):
        raise ForaDoFormato(f"nome de pacote npm inválido: `{pacote}`")
    if PADRAO_DA_VERSAO.match(versao) is None:
        raise ForaDoFormato(f"versão fora do formato x.y.z: `{versao}`")
    if not trecho.strip():
        raise ForaDoFormato(f"trecho vazio em {pacote}@{versao}")
    return BibliotecaSugerida(pacote, versao, trecho)


def nome_de_pacote_npm_valido(pacote: str) -> bool:
    cabe_no_limite = len(pacote) <= TAMANHO_MAXIMO_DO_PACOTE
    return cabe_no_limite and PADRAO_DO_PACOTE.match(pacote) is not None
