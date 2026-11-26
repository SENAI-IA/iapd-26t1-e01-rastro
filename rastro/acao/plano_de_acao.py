from dataclasses import replace

from rastro.acao.acoes_das_bibliotecas import acoes_das_bibliotecas
from rastro.acao.acoes_das_checagens import acoes_das_checagens
from rastro.acao.modelos import Acao
from rastro.acao.texto_da_tarefa import gerar_texto_da_tarefa
from rastro.configuracao.modelos import Checagem
from rastro.explicacao.modelos import Explicacao
from rastro.risco.modelos import Achado
from rastro.risco.prioridade import ORDEM_DA_PRIORIDADE, valor_para_ordem_decrescente


def montar_plano_de_acao(
    achados: list[Achado],
    explicacoes: dict[str, Explicacao],
    checagens: list[Checagem],
) -> list[Acao]:
    acoes = acoes_das_bibliotecas(achados, explicacoes) + acoes_das_checagens(checagens)
    return [com_texto_da_task(acao) for acao in ordenar_acoes(acoes)]


def com_texto_da_task(acao: Acao) -> Acao:
    return replace(acao, texto_task=gerar_texto_da_tarefa(acao))


def ordenar_acoes(acoes: list[Acao]) -> list[Acao]:
    return sorted(acoes, key=chave_da_ordem_da_acao)


def chave_da_ordem_da_acao(acao: Acao) -> tuple[int, bool, float]:
    sem_nota = acao.nota is None
    nota_decrescente = valor_para_ordem_decrescente(acao.nota)
    return (ORDEM_DA_PRIORIDADE[acao.prioridade], sem_nota, nota_decrescente)
