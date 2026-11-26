import json
import re
from typing import Any

TRAVA_FORMATO_FECHADO = "formato fechado"
CERCA_DE_CODIGO = re.compile(
    r"""
    ^ ``` [a-z]* \n
    (?P<conteudo> .* )
    \n ``` $
    """,
    re.VERBOSE | re.DOTALL,
)


class ForaDoFormato(Exception):
    pass


def ler_json_sem_texto_fora(resposta: str) -> object:
    texto = resposta.strip()
    if not texto.startswith("{"):
        raise ForaDoFormato("texto fora do JSON")
    objeto, fim_do_json = ler_json_do_inicio_do_texto(texto)
    if fim_do_json != len(texto):
        raise ForaDoFormato("texto fora do JSON")
    return objeto


def ler_json_do_inicio_do_texto(texto: str) -> tuple[object, int]:
    try:
        return leitor_que_recusa_campo_repetido().raw_decode(texto)
    except json.JSONDecodeError as erro:
        raise ForaDoFormato(f"JSON inválido ({erro.msg})") from erro


def leitor_que_recusa_campo_repetido() -> json.JSONDecoder:
    return json.JSONDecoder(object_pairs_hook=recusar_campo_repetido)


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


def ler_texto(item: dict[str, Any], campo: str) -> str:
    valor = item[campo]
    if not isinstance(valor, str):
        raise ForaDoFormato(f"`{campo}` não é texto")
    return valor


def tirar_cerca_de_codigo(resposta: str) -> str:
    texto = resposta.strip()
    cercado = CERCA_DE_CODIGO.match(texto)
    if cercado is None:
        return texto
    return cercado.group("conteudo")
