from rastro.risco.modelos import Nota
from rastro.risco.nota import calcular_nota, calcular_nota_de_risco


def test_r05_1_cvss_6_1_e_percentil_0_97_da_7_9() -> None:
    assert calcular_nota_de_risco(6.1, 0.97) == 7.9


def test_r05_1_arredonda_meio_para_cima_como_na_conta_feita_a_mao() -> None:
    assert calcular_nota_de_risco(6.1, 0.0) == 3.1


def test_r05_1_percentil_do_epss_com_cinco_casas() -> None:
    assert calcular_nota_de_risco(7.5, 0.21662) == 4.8


def test_r05_1_extremos_da_formula() -> None:
    assert calcular_nota_de_risco(10.0, 1.0) == 10.0
    assert calcular_nota_de_risco(0.0, 0.0) == 0.0


def test_r05_1_nota_com_cvss_e_epss_traz_a_conta_escrita() -> None:
    assert calcular_nota(6.1, 0.97) == Nota(
        valor=7.9,
        prioridade="alta",
        conta="10 × (0,5 × 6,1/10 + 0,5 × 0,97) = 7,9",
        sem_epss=False,
    )


def test_r05_1_conta_mostra_o_percentil_como_veio_da_fonte() -> None:
    assert calcular_nota(7.5, 0.21662).conta == "10 × (0,5 × 7,5/10 + 0,5 × 0,21662) = 4,8"


def test_r05_1_conta_mostra_cvss_e_nota_inteiros_com_uma_casa() -> None:
    assert calcular_nota(10.0, 1.0).conta == "10 × (0,5 × 10,0/10 + 0,5 × 1) = 10,0"


def test_r05_3_sem_epss_a_nota_e_o_cvss() -> None:
    assert calcular_nota(6.1, None) == Nota(
        valor=6.1,
        prioridade="baixa",
        conta="sem EPSS: nota = CVSS = 6,1",
        sem_epss=True,
    )


def test_r05_4_sem_cvss_fica_sem_nota() -> None:
    nota = calcular_nota(None, 0.97)
    assert nota.valor is None
    assert nota.conta == "sem CVSS: sem nota"
    assert nota.sem_epss is False
    assert nota.prioridade == "a avaliar"


def test_r05_4_sem_cvss_e_sem_epss_fica_sem_nota_e_com_selo() -> None:
    assert calcular_nota(None, None) == Nota(
        valor=None,
        prioridade="a avaliar",
        conta="sem CVSS: sem nota",
        sem_epss=True,
    )
