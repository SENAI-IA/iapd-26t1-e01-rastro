from rastro.relatorio.montagem_do_relatorio import montar_relatorio
from tests.dubles import ConectorFalso, analise_da_loja, relatorio_da_loja


def test_r13_7_resumo_traz_pronta_cada_contagem_da_tela() -> None:
    resumo = relatorio_da_loja()["resumo"]

    assert resumo == {
        "nota_maxima": 8.3,
        "acoes": 7,
        "acoes_por_prioridade": {"alta": 1, "media": 3, "baixa": 3, "a avaliar": 0},
        "bibliotecas": 2,
        "bibliotecas_vulneraveis": 1,
        "bibliotecas_a_confirmar": 0,
        "bibliotecas_nao_consultadas": 0,
        "achados": 2,
        "checagens_com_falha": 6,
        "checagens_nao_verificadas": 0,
        "encontradas_so_pela_ia": None,
    }


def test_r13_7_resumo_sem_achados_fica_sem_nota_maxima() -> None:
    fonte = ConectorFalso(sem_resposta_para=frozenset({"jquery"}))
    resumo = montar_relatorio(analise_da_loja(fonte))["resumo"]

    assert resumo["nota_maxima"] is None
    assert resumo["bibliotecas_vulneraveis"] == 0
    assert resumo["bibliotecas_nao_consultadas"] == 1


def test_r14_6_sem_ia_encontradas_so_pela_ia_e_nao_procurado_e_nao_zero() -> None:
    assert relatorio_da_loja()["resumo"]["encontradas_so_pela_ia"] is None
