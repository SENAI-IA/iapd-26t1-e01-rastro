from rastro.fontes.filtro_do_pacote_npm import pacote_e_o_npm_procurado


def test_r04_1_aceita_o_pacote_npm_de_mesmo_nome() -> None:
    assert pacote_e_o_npm_procurado({"ecosystem": "npm", "name": "jquery"}, "jquery")


def test_r04_1_recusa_pacote_de_outro_ecossistema() -> None:
    assert not pacote_e_o_npm_procurado({"ecosystem": "PyPI", "name": "jquery"}, "jquery")


def test_r04_1_recusa_pacote_npm_de_outro_nome() -> None:
    assert not pacote_e_o_npm_procurado({"ecosystem": "npm", "name": "jquery-ui"}, "jquery")
