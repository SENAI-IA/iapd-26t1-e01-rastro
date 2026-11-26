from rastro.acao.acoes_das_checagens import (
    acao_da_checagem,
    acoes_das_checagens,
    porque_da_checagem,
)
from rastro.acao.correcoes_das_checagens import CORRECOES_DAS_CHECAGENS
from rastro.configuracao.modelos import Checagem, SituacaoDaChecagem
from rastro.configuracao.regras_das_checagens import COOKIE_SEM_SECURE, CSP_AUSENTE


def checagem(situacao: SituacaoDaChecagem = "falhou") -> Checagem:
    return Checagem(
        id=CSP_AUSENTE.id,
        titulo=CSP_AUSENTE.titulo,
        situacao=situacao,
        severidade=CSP_AUSENTE.severidade,
        quem_resolve=CSP_AUSENTE.quem_resolve,
        evidencia=None,
        detalhe="a página não envia Content-Security-Policy: https://loja.exemplo/",
    )


def test_r08_2_so_checagem_que_falhou_vira_acao() -> None:
    checagens = [checagem("passou"), checagem("nao_verificada"), checagem()]

    assert [acao.id for acao in acoes_das_checagens(checagens)] == ["C01"]


def test_r08_3_acao_da_checagem_usa_a_correcao_e_a_severidade_da_regra() -> None:
    acao = acao_da_checagem(checagem())

    assert acao.o_que_fazer == CORRECOES_DAS_CHECAGENS["C01"].o_que_fazer
    assert acao.impacto == CORRECOES_DAS_CHECAGENS["C01"].impacto
    assert acao.prioridade == "media"
    assert acao.nota is None
    assert acao.refs == ["C01"]
    assert acao.teste_verificacao is None


def test_r08_3_porque_da_checagem_traz_regra_severidade_e_detalhe() -> None:
    assert porque_da_checagem(checagem()) == (
        "Regra C01 (CSP ausente), severidade média: "
        "a página não envia Content-Security-Policy: https://loja.exemplo/"
    )


def test_r08_2_toda_regra_de_cookie_tem_correcao() -> None:
    assert COOKIE_SEM_SECURE.id in CORRECOES_DAS_CHECAGENS
