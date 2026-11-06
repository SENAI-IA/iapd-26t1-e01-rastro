import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from rastro.har.modelos import Requisicao
from rastro.identificacao.modelos import Biblioteca, Evidencia

VERSAO = r"(\d+\.\d+\.\d+)"
INICIO_DO_NOME = r"(?<![\w-])"
SEPARADOR_DA_VERSAO = r"(?:[-.@/]?|(?:\.min)?\.js\?v(?:er)?=)"


@dataclass(frozen=True)
class Assinatura:
    pacote: str
    nome_no_arquivo: str
    comentario_de_versao: str | None


ASSINATURAS: tuple[Assinatura, ...] = (
    Assinatura("jquery", r"jquery", rf"jQuery (?:JavaScript Library )?v{VERSAO}"),
    Assinatura("jquery-ui", r"jquery-ui", rf"jQuery UI - v{VERSAO}"),
    Assinatura("bootstrap", r"bootstrap", rf"Bootstrap v{VERSAO}"),
    Assinatura("lodash", r"lodash", rf"lodash (?:lodash\.com/license | )?v?{VERSAO}"),
    Assinatura("moment", r"moment", rf"//! version : {VERSAO}"),
    Assinatura("angular", r"angular", rf"AngularJS v{VERSAO}"),
    Assinatura("underscore", r"underscore", rf"Underscore\.js {VERSAO}"),
    Assinatura("requirejs", r"requirejs", rf"@license RequireJS {VERSAO}"),
    Assinatura("ckeditor", r"ckeditor", None),
)


def identificar_pelo_nome_do_arquivo(requisicoes: list[Requisicao]) -> list[Biblioteca]:
    bibliotecas: list[Biblioteca] = []
    for requisicao in requisicoes:
        if e_script(requisicao):
            bibliotecas.extend(bibliotecas_no_nome_do_arquivo(requisicao))
    return bibliotecas


def bibliotecas_no_nome_do_arquivo(requisicao: Requisicao) -> list[Biblioteca]:
    nome_do_arquivo = caminho_com_parametros(requisicao.url)
    bibliotecas: list[Biblioteca] = []
    for assinatura in ASSINATURAS:
        versao = versao_no_nome_do_arquivo(assinatura, nome_do_arquivo)
        if versao is not None:
            bibliotecas.append(biblioteca_pela_url(assinatura.pacote, versao, requisicao))
    return bibliotecas


def versao_no_nome_do_arquivo(assinatura: Assinatura, nome_do_arquivo: str) -> str | None:
    padrao = INICIO_DO_NOME + assinatura.nome_no_arquivo + SEPARADOR_DA_VERSAO + VERSAO
    encontrado = re.search(padrao, nome_do_arquivo, re.IGNORECASE)
    if encontrado is None:
        return None
    return encontrado.group(1)


def biblioteca_pela_url(pacote: str, versao: str, requisicao: Requisicao) -> Biblioteca:
    evidencia = Evidencia(indice_requisicao=requisicao.indice, url=requisicao.url, trecho=None)
    return Biblioteca(
        pacote=pacote,
        versao=versao,
        metodo="assinatura",
        situacao="confirmada",
        conferida_no_npm=None,
        travas_que_falharam=[],
        evidencias=[evidencia],
    )


def e_script(requisicao: Requisicao) -> bool:
    tipo_conteudo = requisicao.tipo_conteudo or ""
    caminho = urlsplit(requisicao.url).path.lower()
    return tipo_conteudo.endswith("javascript") or caminho.endswith(".js")


def caminho_com_parametros(url: str) -> str:
    partes = urlsplit(url)
    if partes.query:
        return f"{partes.path}?{partes.query}"
    return partes.path
