from dataclasses import asdict, replace
from typing import Any

from rastro.har.site import url_sem_valores_da_query
from rastro.har.visita import PassoDaVisita
from rastro.identificacao.modelos import Biblioteca, nome_com_versao
from rastro.modelos_da_analise import Analise
from rastro.risco.achados import achados_da_biblioteca
from rastro.risco.modelos import Achado, Prioridade
from rastro.risco.prioridade import PRIORIDADES, classificar_prioridade, nota_da_biblioteca


def montar_visita_no_relatorio(analise: Analise) -> list[dict[str, Any]]:
    bibliotecas_por_requisicao = agrupar_bibliotecas_por_requisicao(analise.bibliotecas)
    return [
        passo_no_relatorio(
            passo, bibliotecas_por_requisicao.get(passo.indice_requisicao, []), analise.achados
        )
        for passo in analise.visita
    ]


def agrupar_bibliotecas_por_requisicao(bibliotecas: list[Biblioteca]) -> dict[int, list[str]]:
    agrupadas: dict[int, list[str]] = {}
    for biblioteca in bibliotecas:
        for indice in {evidencia.indice_requisicao for evidencia in biblioteca.evidencias}:
            agrupadas.setdefault(indice, []).append(nome_com_versao(biblioteca))
    return agrupadas


def passo_no_relatorio(
    passo: PassoDaVisita, chaves: list[str], achados: list[Achado]
) -> dict[str, Any]:
    prioridades = [prioridade_da_biblioteca(chave, achados) for chave in chaves]
    return {
        **asdict(replace(passo, url=url_sem_valores_da_query(passo.url))),
        "bibliotecas": chaves,
        "prioridade": prioridade_mais_alta(prioridades),
    }


def prioridade_da_biblioteca(chave: str, achados: list[Achado]) -> Prioridade | None:
    achados_da_chave = achados_da_biblioteca(chave, achados)
    if not achados_da_chave:
        return None
    return classificar_prioridade(nota_da_biblioteca(achados_da_chave))


def prioridade_mais_alta(prioridades: list[Prioridade | None]) -> Prioridade | None:
    for prioridade in PRIORIDADES:
        if prioridade in prioridades:
            return prioridade
    return None
