import base64
import binascii
import json
from pathlib import Path
from typing import Any

from rastro.har.modelos import Cookie, Requisicao

MENSAGEM_HAR_INVALIDO = "o arquivo não é um HAR válido"


class ErroAoLerHar(Exception):
    pass


class HarNaoEncontrado(ErroAoLerHar):
    def __init__(self, caminho: Path) -> None:
        super().__init__(f"HAR não encontrado: {caminho}")


class HarInvalido(ErroAoLerHar):
    def __init__(self) -> None:
        super().__init__(MENSAGEM_HAR_INVALIDO)


def ler_har(caminho: Path) -> list[Requisicao]:
    har = carregar_json(caminho)
    requisicoes = []
    for indice, entrada in enumerate(extrair_entradas(har)):
        requisicoes.append(converter_entrada(indice, entrada))
    return requisicoes


def carregar_json(caminho: Path) -> Any:
    if not caminho.is_file():
        raise HarNaoEncontrado(caminho)
    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (UnicodeDecodeError, json.JSONDecodeError) as erro:
        raise HarInvalido() from erro


def extrair_entradas(har: Any) -> list[dict[str, Any]]:
    if not isinstance(har, dict) or not isinstance(har.get("log"), dict):
        raise HarInvalido()
    entradas = har["log"].get("entries")
    if not isinstance(entradas, list):
        raise HarInvalido()
    for entrada in entradas:
        if not entrada_e_valida(entrada):
            raise HarInvalido()
    return entradas


def entrada_e_valida(entrada: Any) -> bool:
    if not isinstance(entrada, dict):
        return False
    pedido = entrada.get("request")
    resposta = entrada.get("response")
    if not isinstance(pedido, dict) or not isinstance(resposta, dict):
        return False
    return (
        isinstance(pedido.get("url"), str)
        and isinstance(pedido.get("method"), str)
        and isinstance(resposta.get("status"), int)
    )


def converter_entrada(indice: int, entrada: dict[str, Any]) -> Requisicao:
    pedido = entrada["request"]
    resposta = entrada["response"]
    cabecalhos = ler_cabecalhos(resposta)
    conteudo_da_resposta = resposta.get("content") or {}
    return Requisicao(
        indice=indice,
        url=pedido["url"],
        metodo=pedido["method"],
        status=resposta["status"],
        tipo_conteudo=ler_tipo_de_conteudo(conteudo_da_resposta, cabecalhos),
        cabecalhos_resposta=cabecalhos,
        cookies_resposta=ler_cookies(resposta),
        conteudo=ler_conteudo(conteudo_da_resposta),
    )


def ler_cabecalhos(resposta: dict[str, Any]) -> dict[str, str]:
    cabecalhos: dict[str, str] = {}
    for nome, valor in pares_de_cabecalho(resposta):
        if nome == "set-cookie":
            continue
        if nome in cabecalhos:
            cabecalhos[nome] = f"{cabecalhos[nome]}, {valor}"
        else:
            cabecalhos[nome] = valor
    return cabecalhos


def pares_de_cabecalho(resposta: dict[str, Any]) -> list[tuple[str, str]]:
    pares = []
    for cabecalho in resposta.get("headers") or []:
        nome = str(cabecalho.get("name", "")).strip().lower()
        valor = str(cabecalho.get("value", ""))
        pares.append((nome, valor))
    return pares


def ler_tipo_de_conteudo(
    conteudo_da_resposta: dict[str, Any], cabecalhos: dict[str, str]
) -> str | None:
    tipo = conteudo_da_resposta.get("mimeType") or cabecalhos.get("content-type") or ""
    tipo_sem_parametros = str(tipo).split(";")[0].strip().lower()
    return tipo_sem_parametros or None


def ler_conteudo(conteudo_da_resposta: dict[str, Any]) -> str | None:
    texto = conteudo_da_resposta.get("text")
    if not isinstance(texto, str):
        return None
    if conteudo_da_resposta.get("encoding") == "base64":
        return decodificar_base64(texto)
    return texto


def decodificar_base64(texto: str) -> str | None:
    try:
        dados = base64.b64decode(texto)
    except binascii.Error:
        return None
    return dados.decode("utf-8", errors="replace")


def ler_cookies(resposta: dict[str, Any]) -> list[Cookie]:
    cookies_do_har = resposta.get("cookies") or []
    if cookies_do_har:
        return [converter_cookie_do_har(cookie) for cookie in cookies_do_har]
    cookies = []
    for linha in linhas_de_set_cookie(resposta):
        cookie = interpretar_set_cookie(linha)
        if cookie is not None:
            cookies.append(cookie)
    return cookies


def converter_cookie_do_har(cookie: dict[str, Any]) -> Cookie:
    return Cookie(
        nome=str(cookie.get("name", "")),
        http_only=bool(cookie.get("httpOnly", False)),
        secure=bool(cookie.get("secure", False)),
        same_site=cookie.get("sameSite") or None,
    )


def linhas_de_set_cookie(resposta: dict[str, Any]) -> list[str]:
    linhas: list[str] = []
    for nome, valor in pares_de_cabecalho(resposta):
        if nome == "set-cookie":
            linhas.extend(valor.split("\n"))
    return linhas


def interpretar_set_cookie(linha: str) -> Cookie | None:
    nome_e_valor, *atributos = linha.split(";")
    nome = nome_e_valor.split("=", 1)[0].strip()
    if not nome:
        return None
    http_only = False
    secure = False
    same_site = None
    for atributo in atributos:
        chave, _, valor = atributo.partition("=")
        chave = chave.strip().lower()
        if chave == "httponly":
            http_only = True
        elif chave == "secure":
            secure = True
        elif chave == "samesite":
            same_site = valor.strip() or None
    return Cookie(nome=nome, http_only=http_only, secure=secure, same_site=same_site)
