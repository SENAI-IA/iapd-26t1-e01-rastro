from typing import Any

from rastro.acao.modelos import Acao
from rastro.configuracao.modelos import SituacaoDaChecagem
from rastro.identificacao.modelos import nome_com_versao
from rastro.modelos_da_analise import Analise
from rastro.risco.modelos import Achado
from rastro.risco.prioridade import PRIORIDADES, nota_da_biblioteca


def montar_resumo(analise: Analise) -> dict[str, Any]:
    return {
        "nota_maxima": nota_da_biblioteca(analise.achados),
        "acoes": len(analise.plano_de_acao),
        "acoes_por_prioridade": contar_acoes_por_prioridade(analise.plano_de_acao),
        "bibliotecas": len(analise.bibliotecas),
        "bibliotecas_vulneraveis": len(chaves_das_bibliotecas_com_achados(analise.achados)),
        "bibliotecas_a_confirmar": len(analise.a_confirmar),
        "bibliotecas_nao_consultadas": len(analise.nao_consultadas),
        "achados": len(analise.achados),
        "checagens_com_falha": contar_checagens(analise, "falhou"),
        "checagens_nao_verificadas": contar_checagens(analise, "nao_verificada"),
        "encontradas_so_pela_ia": encontradas_so_pela_ia(analise),
    }


def contar_acoes_por_prioridade(acoes: list[Acao]) -> dict[str, int]:
    contagem: dict[str, int] = {prioridade: 0 for prioridade in PRIORIDADES}
    for acao in acoes:
        contagem[acao.prioridade] += 1
    return contagem


def chaves_das_bibliotecas_com_achados(achados: list[Achado]) -> set[str]:
    return {nome_com_versao(achado.biblioteca) for achado in achados}


def contar_checagens(analise: Analise, situacao: SituacaoDaChecagem) -> int:
    return sum(1 for checagem in analise.checagens if checagem.situacao == situacao)


def encontradas_so_pela_ia(analise: Analise) -> int | None:
    if analise.provedor_de_ia is None:
        return None
    return sum(1 for biblioteca in analise.bibliotecas if biblioteca.metodo == "ia")
