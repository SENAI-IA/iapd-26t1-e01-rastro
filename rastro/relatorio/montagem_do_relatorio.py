from dataclasses import asdict, replace
from typing import Any

from rastro.configuracao.modelos import Checagem
from rastro.har.site import url_sem_valores_da_query
from rastro.identificacao.modelos import Biblioteca, Evidencia, nome_com_versao
from rastro.modelos_da_analise import Analise
from rastro.pentest.modelos import ResultadoDoPentest
from rastro.relatorio.limitacoes_da_analise import continua_igual, listar_limitacoes
from rastro.relatorio.painel_da_ia import montar_painel_da_ia
from rastro.relatorio.resumo_do_relatorio import montar_resumo
from rastro.relatorio.visita_no_relatorio import montar_visita_no_relatorio
from rastro.risco.achados import achados_da_biblioteca
from rastro.risco.modelos import Achado
from rastro.risco.prioridade import classificar_prioridade, nota_da_biblioteca

VERSAO_DO_FORMATO = 1


def montar_relatorio(analise: Analise, pentest: ResultadoDoPentest | None = None) -> dict[str, Any]:
    return {
        "versao_formato": VERSAO_DO_FORMATO,
        "analise": dados_da_analise(analise),
        "resumo": montar_resumo(analise),
        "bibliotecas": [
            biblioteca_no_relatorio(biblioteca, analise) for biblioteca in analise.bibliotecas
        ],
        "a_confirmar": [
            biblioteca_no_relatorio(biblioteca, analise) for biblioteca in analise.a_confirmar
        ],
        "achados": [achado_no_relatorio(achado) for achado in analise.achados],
        "checagens": [checagem_no_relatorio(checagem) for checagem in analise.checagens],
        "plano_de_acao": [asdict(acao) for acao in analise.plano_de_acao],
        "ia": montar_painel_da_ia(analise),
        "visita": montar_visita_no_relatorio(analise),
        "pentest": pentest_no_relatorio(pentest),
    }


def pentest_no_relatorio(pentest: ResultadoDoPentest | None) -> dict[str, Any] | None:
    if pentest is None:
        return None
    return asdict(pentest)


def dados_da_analise(analise: Analise) -> dict[str, Any]:
    return {
        "har": analise.har,
        "site": analise.site,
        "data": analise.inicio.isoformat(timespec="seconds"),
        "ia": analise.provedor_de_ia,
        "limitacoes": listar_limitacoes(analise),
        "continua_igual": continua_igual(analise),
        "duracao_s": analise.duracao_s,
    }


def biblioteca_no_relatorio(biblioteca: Biblioteca, analise: Analise) -> dict[str, Any]:
    chave = nome_com_versao(biblioteca)
    achados = achados_da_biblioteca(chave, analise.achados)
    explicacao = analise.explicacoes.get(chave)
    nota = nota_da_biblioteca(achados)
    return {
        "id": chave,
        **asdict(replace(biblioteca, evidencias=evidencias_sem_valores(biblioteca.evidencias))),
        "nota": nota,
        "prioridade": classificar_prioridade(nota) if achados else None,
        "achados": [achado.aviso.ghsa for achado in achados],
        "motivo_nao_consultada": analise.nao_consultadas.get(chave),
        "explicacao": asdict(explicacao) if explicacao is not None else None,
    }


def evidencias_sem_valores(evidencias: list[Evidencia]) -> list[Evidencia]:
    return [evidencia_sem_valores(evidencia) for evidencia in evidencias]


def evidencia_sem_valores(evidencia: Evidencia) -> Evidencia:
    return replace(evidencia, url=url_sem_valores_da_query(evidencia.url))


def checagem_no_relatorio(checagem: Checagem) -> dict[str, Any]:
    if checagem.evidencia is None:
        return asdict(checagem)
    return asdict(replace(checagem, evidencia=evidencia_sem_valores(checagem.evidencia)))


def achado_no_relatorio(achado: Achado) -> dict[str, Any]:
    return {
        "biblioteca": nome_com_versao(achado.biblioteca),
        "aviso": asdict(achado.aviso),
        "nota": asdict(achado.nota),
    }
