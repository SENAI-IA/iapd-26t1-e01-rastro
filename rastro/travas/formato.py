import json
import re
from dataclasses import dataclass
from typing import Any

from rastro.travas.modelos import TravaAcionada

NOME_DA_TRAVA = "formato fechado"
ALVO = "resposta da IA"
CAMPOS_DA_RESPOSTA = {"bibliotecas"}
CAMPOS_DA_BIBLIOTECA = {"pacote", "versao", "trecho"}
TAMANHO_MAXIMO_DO_PACOTE = 214
PADRAO_DO_PACOTE = re.compile(r"^(?:@[a-z0-9~-][a-z0-9._~-]*/)?[a-z0-9~-][a-z0-9._~-]*$")
PADRAO_DA_VERSAO = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


class ForaDoFormato(Exception):
    pass


@dataclass(frozen=True)
class BibliotecaSugerida:
    pacote: str
    versao: str
    trecho: str


def conferir_formato(resposta: str) -> tuple[list[BibliotecaSugerida], list[TravaAcionada]]:
    try:
        return ler_bibliotecas_sugeridas(resposta), []
    except ForaDoFormato as erro:
        return [], [TravaAcionada(NOME_DA_TRAVA, ALVO, f"resposta descartada: {erro}")]


def ler_bibliotecas_sugeridas(resposta: str) -> list[BibliotecaSugerida]:
    objeto = exigir_campos(ler_json_sem_texto_fora(resposta), CAMPOS_DA_RESPOSTA, "na resposta")
    bibliotecas = objeto["bibliotecas"]
    if not isinstance(bibliotecas, list):
        raise ForaDoFormato("`bibliotecas` não é uma lista")
    return [ler_biblioteca(item) for item in bibliotecas]


def ler_json_sem_texto_fora(resposta: str) -> object:
    texto = resposta.strip()
    if not texto.startswith("{"):
        raise ForaDoFormato("texto fora do JSON")
    decodificador = json.JSONDecoder(object_pairs_hook=recusar_campo_repetido)
    try:
        objeto, fim = decodificador.raw_decode(texto)
    except json.JSONDecodeError as erro:
        raise ForaDoFormato(f"JSON inválido ({erro.msg})") from erro
    if fim != len(texto):
        raise ForaDoFormato("texto fora do JSON")
    return objeto


def recusar_campo_repetido(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    objeto: dict[str, Any] = {}
    for campo, valor in pares:
        if campo in objeto:
            raise ForaDoFormato(f"campo repetido: `{campo}`")
        objeto[campo] = valor
    return objeto


def exigir_campos(objeto: object, esperados: set[str], onde: str) -> dict[str, Any]:
    if not isinstance(objeto, dict):
        raise ForaDoFormato(f"esperado um objeto {onde}")
    a_mais = sorted(set(objeto) - esperados)
    faltando = sorted(esperados - set(objeto))
    if a_mais:
        raise ForaDoFormato(f"campo a mais {onde}: {', '.join(a_mais)}")
    if faltando:
        raise ForaDoFormato(f"campo faltando {onde}: {', '.join(faltando)}")
    return objeto


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


def ler_texto(item: dict[str, Any], campo: str) -> str:
    valor = item[campo]
    if not isinstance(valor, str):
        raise ForaDoFormato(f"`{campo}` não é texto")
    return valor


def nome_de_pacote_npm_valido(pacote: str) -> bool:
    cabe_no_limite = len(pacote) <= TAMANHO_MAXIMO_DO_PACOTE
    return cabe_no_limite and PADRAO_DO_PACOTE.match(pacote) is not None
