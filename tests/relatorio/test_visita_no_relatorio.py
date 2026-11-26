from tests.dubles import relatorio_da_loja


def test_r22_2_visita_liga_cada_requisicao_a_biblioteca_e_a_prioridade() -> None:
    visita = relatorio_da_loja()["visita"]

    com_biblioteca = [passo for passo in visita if passo["bibliotecas"]]
    assert [passo["bibliotecas"] for passo in com_biblioteca] == [
        ["jquery@3.4.1"],
        ["lodash@4.17.21"],
    ]
    assert com_biblioteca[0]["prioridade"] is not None
    assert com_biblioteca[1]["prioridade"] is None
    assert all("?" not in passo["url"] or "[removido]" in passo["url"] for passo in visita)
