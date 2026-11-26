from rastro.acao.correcoes_das_checagens import CORRECOES_DAS_CHECAGENS
from rastro.acao.modelos import Acao
from rastro.configuracao.modelos import Checagem
from rastro.risco.prioridade import ROTULO_DA_PRIORIDADE


def acoes_das_checagens(checagens: list[Checagem]) -> list[Acao]:
    return [acao_da_checagem(checagem) for checagem in checagens if checagem.situacao == "falhou"]


def acao_da_checagem(checagem: Checagem) -> Acao:
    correcao = CORRECOES_DAS_CHECAGENS[checagem.id]
    return Acao(
        id=checagem.id,
        prioridade=checagem.severidade,
        nota=None,
        o_que_fazer=correcao.o_que_fazer,
        porque=porque_da_checagem(checagem),
        impacto=correcao.impacto,
        quem_resolve=checagem.quem_resolve,
        refs=[checagem.id],
        teste_verificacao=None,
    )


def porque_da_checagem(checagem: Checagem) -> str:
    severidade = ROTULO_DA_PRIORIDADE[checagem.severidade]
    return f"Regra {checagem.id} ({checagem.titulo}), severidade {severidade}: {checagem.detalhe}"
