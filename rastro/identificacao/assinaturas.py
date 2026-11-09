import re
from dataclasses import dataclass, replace
from urllib.parse import urlsplit

from rastro.har.modelos import Requisicao
from rastro.identificacao.modelos import Biblioteca, Evidencia

VERSAO = r"(\d+\.\d+\.\d+)"
INICIO_DO_NOME = r"(?<![\w-])"
SEPARADOR_DA_VERSAO = r"(?:[-.@/]?|(?:\.min)?\.js\?v(?:er)?=)"
INICIO_DO_COMENTARIO = r"(?:/\*[*!]?\s*|//!?[ \t]*|^[ \t]*\*[ \t]*)"


@dataclass(frozen=True)
class Assinatura:
    pacote: str
    nome_no_arquivo: str
    comentario_de_versao: str | None


ASSINATURAS: tuple[Assinatura, ...] = (
    Assinatura("jquery", r"jquery", rf"jQuery (?:JavaScript Library )?v{VERSAO}"),
    Assinatura("jquery-ui", r"jquery-ui", rf"jQuery UI - v{VERSAO}"),
    Assinatura("bootstrap", r"bootstrap", rf"Bootstrap v{VERSAO}"),
    Assinatura("lodash", r"lodash", rf"lodash {VERSAO}"),
    Assinatura("moment", r"moment", rf"moment\.js\s*//! version : {VERSAO}"),
    Assinatura("angular", r"angular", rf"(?:@license )?AngularJS v{VERSAO}"),
    Assinatura("underscore", r"underscore", rf"Underscore\.js {VERSAO}"),
    Assinatura("requirejs", r"requirejs", rf"@license RequireJS {VERSAO}"),
    Assinatura("ckeditor", r"ckeditor", None),
)


def identificar_por_assinatura(requisicoes: list[Requisicao]) -> list[Biblioteca]:
    bibliotecas: list[Biblioteca] = []
    for requisicao in requisicoes:
        if e_script(requisicao):
            bibliotecas.extend(bibliotecas_na_requisicao(requisicao))
    return agrupar_repetidas(bibliotecas)


def bibliotecas_na_requisicao(requisicao: Requisicao) -> list[Biblioteca]:
    bibliotecas: list[Biblioteca] = []
    for assinatura in ASSINATURAS:
        pelo_comentario = bibliotecas_no_comentario(assinatura, requisicao)
        if pelo_comentario:
            bibliotecas.extend(pelo_comentario)
        else:
            bibliotecas.extend(bibliotecas_no_nome_do_arquivo(assinatura, requisicao))
    return bibliotecas


def bibliotecas_no_comentario(assinatura: Assinatura, requisicao: Requisicao) -> list[Biblioteca]:
    if assinatura.comentario_de_versao is None or requisicao.conteudo is None:
        return []
    padrao = INICIO_DO_COMENTARIO + assinatura.comentario_de_versao
    bibliotecas: list[Biblioteca] = []
    for encontrado in re.finditer(padrao, requisicao.conteudo, re.MULTILINE):
        versao = encontrado.group(1)
        trecho = encontrado.group(0).strip()
        bibliotecas.append(biblioteca_por_assinatura(assinatura.pacote, versao, requisicao, trecho))
    return bibliotecas


def bibliotecas_no_nome_do_arquivo(
    assinatura: Assinatura, requisicao: Requisicao
) -> list[Biblioteca]:
    versao = versao_no_nome_do_arquivo(assinatura, caminho_com_parametros(requisicao.url))
    if versao is None:
        return []
    return [biblioteca_por_assinatura(assinatura.pacote, versao, requisicao, trecho=None)]


def versao_no_nome_do_arquivo(assinatura: Assinatura, nome_do_arquivo: str) -> str | None:
    padrao = INICIO_DO_NOME + assinatura.nome_no_arquivo + SEPARADOR_DA_VERSAO + VERSAO
    encontrado = re.search(padrao, nome_do_arquivo, re.IGNORECASE)
    if encontrado is None:
        return None
    return encontrado.group(1)


def biblioteca_por_assinatura(
    pacote: str, versao: str, requisicao: Requisicao, trecho: str | None
) -> Biblioteca:
    evidencia = Evidencia(indice_requisicao=requisicao.indice, url=requisicao.url, trecho=trecho)
    return Biblioteca(
        pacote=pacote,
        versao=versao,
        metodo="assinatura",
        situacao="confirmada",
        conferida_no_npm=None,
        travas_que_falharam=[],
        evidencias=[evidencia],
    )


def agrupar_repetidas(bibliotecas: list[Biblioteca]) -> list[Biblioteca]:
    agrupadas: dict[tuple[str, str], Biblioteca] = {}
    for biblioteca in bibliotecas:
        chave = (biblioteca.pacote, biblioteca.versao)
        if chave in agrupadas:
            agrupadas[chave] = juntar_evidencias(agrupadas[chave], biblioteca)
        else:
            agrupadas[chave] = biblioteca
    return list(agrupadas.values())


def juntar_evidencias(primeira: Biblioteca, repetida: Biblioteca) -> Biblioteca:
    evidencias = list(primeira.evidencias)
    for evidencia in repetida.evidencias:
        if not requisicao_ja_esta_nas_evidencias(evidencia, evidencias):
            evidencias.append(evidencia)
    return replace(primeira, evidencias=evidencias)


def requisicao_ja_esta_nas_evidencias(evidencia: Evidencia, evidencias: list[Evidencia]) -> bool:
    for existente in evidencias:
        if existente.indice_requisicao == evidencia.indice_requisicao:
            return True
    return False


def e_script(requisicao: Requisicao) -> bool:
    tipo_conteudo = requisicao.tipo_conteudo or ""
    caminho = urlsplit(requisicao.url).path.lower()
    return tipo_conteudo.endswith("javascript") or caminho.endswith(".js")


def caminho_com_parametros(url: str) -> str:
    partes = urlsplit(url)
    if partes.query:
        return f"{partes.path}?{partes.query}"
    return partes.path
