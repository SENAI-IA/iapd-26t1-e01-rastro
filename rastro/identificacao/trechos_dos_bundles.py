import re
from dataclasses import dataclass

from rastro.har.modelos import Requisicao
from rastro.identificacao.assinaturas import requisicao_e_script
from rastro.identificacao.modelos import Biblioteca

TAMANHO_MINIMO_DO_BUNDLE_EM_KILOBYTES = 30
BYTES_POR_KILOBYTE = 1024
TAMANHO_DA_JANELA = 300
MAXIMO_DE_TRECHOS_POR_BUNDLE = 5
COMENTARIO_DE_LICENCA = re.compile(
    r"""
    /\*!
    (?P<texto> .*? )
    \*/
    """,
    re.VERBOSE | re.DOTALL,
)
VERSAO_ENTRE_ASPAS = re.compile(
    r"""
    ["'`]
    v?
    \d+ \. \d+ \. \d+
    (?: - [\w.]+ )?
    ["'`]
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class Bundle:
    requisicao: Requisicao
    trechos: list[str]


def escolher_bundles(
    requisicoes: list[Requisicao], bibliotecas_por_assinatura: list[Biblioteca]
) -> list[Bundle]:
    com_assinatura = indices_com_assinatura(bibliotecas_por_assinatura)
    bundles: list[Bundle] = []
    conteudos_vistos: set[str] = set()
    for requisicao in requisicoes:
        if not bundle_sem_assinatura(requisicao, com_assinatura):
            continue
        conteudo = conteudo_da_requisicao(requisicao)
        if conteudo in conteudos_vistos:
            continue
        conteudos_vistos.add(conteudo)
        bundles.append(Bundle(requisicao, extrair_trechos(conteudo)))
    return bundles


def indices_com_assinatura(bibliotecas: list[Biblioteca]) -> set[int]:
    indices = set()
    for biblioteca in bibliotecas:
        for evidencia in biblioteca.evidencias:
            indices.add(evidencia.indice_requisicao)
    return indices


def bundle_sem_assinatura(requisicao: Requisicao, indices_com_assinatura: set[int]) -> bool:
    if requisicao.indice in indices_com_assinatura:
        return False
    return requisicao_e_bundle(requisicao)


def conteudo_da_requisicao(requisicao: Requisicao) -> str:
    if requisicao.conteudo is None:
        return ""
    return requisicao.conteudo


def requisicao_e_bundle(requisicao: Requisicao) -> bool:
    if not requisicao_e_script(requisicao) or requisicao.conteudo is None:
        return False
    tamanho_em_bytes = len(requisicao.conteudo.encode("utf-8"))
    return tamanho_em_bytes > TAMANHO_MINIMO_DO_BUNDLE_EM_KILOBYTES * BYTES_POR_KILOBYTE


def extrair_trechos(conteudo: str) -> list[str]:
    trechos: list[str] = []
    for trecho in comentarios_de_licenca(conteudo) + janelas_em_volta_de_versoes(conteudo):
        if trecho not in trechos:
            trechos.append(trecho)
    return trechos[:MAXIMO_DE_TRECHOS_POR_BUNDLE]


def comentarios_de_licenca(conteudo: str) -> list[str]:
    comentarios = []
    for encontrado in COMENTARIO_DE_LICENCA.finditer(conteudo):
        if encontrado.group("texto").strip():
            comentarios.append(encontrado.group()[:TAMANHO_DA_JANELA])
    return comentarios


def janelas_em_volta_de_versoes(conteudo: str) -> list[str]:
    janelas = []
    fim_da_ultima_janela = 0
    for encontrado in VERSAO_ENTRE_ASPAS.finditer(conteudo):
        if encontrado.start() < fim_da_ultima_janela:
            continue
        inicio, fim = limites_da_janela(encontrado, len(conteudo))
        janelas.append(conteudo[inicio:fim])
        fim_da_ultima_janela = fim
    return janelas


def limites_da_janela(versao: re.Match[str], tamanho_do_conteudo: int) -> tuple[int, int]:
    meio = (versao.start() + versao.end()) // 2
    inicio = max(0, meio - TAMANHO_DA_JANELA // 2)
    fim = min(tamanho_do_conteudo, inicio + TAMANHO_DA_JANELA)
    return inicio, fim
