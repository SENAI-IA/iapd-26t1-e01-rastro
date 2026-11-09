from rastro.fontes.conector import Aviso
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado
from rastro.risco.nota import calcular_nota
from rastro.risco.prioridade import (
    classificar_prioridade,
    nota_da_biblioteca,
    ordenar_achados,
)

JQUERY = Biblioteca(
    pacote="jquery",
    versao="3.4.1",
    metodo="assinatura",
    situacao="confirmada",
    conferida_no_npm=None,
    travas_que_falharam=[],
    evidencias=[],
)


def achado(ghsa: str, cvss: float | None, percentil_epss: float | None) -> Achado:
    aviso = Aviso(
        fontes=["GitHub Advisory"],
        apelidos=[],
        ghsa=ghsa,
        cve=None,
        resumo="Resumo do aviso",
        cvss=cvss,
        percentil_epss=percentil_epss,
        versoes_afetadas=">= 1.2.0, < 3.5.0",
        versao_corrigida="3.5.0",
        link=f"https://github.com/advisories/{ghsa}",
    )
    return Achado(biblioteca=JQUERY, aviso=aviso, nota=calcular_nota(cvss, percentil_epss))


def ghsas(achados: list[Achado]) -> list[str]:
    return [achado.aviso.ghsa for achado in achados]


def test_r05_2_prioridade_alta_a_partir_de_7_5() -> None:
    assert classificar_prioridade(7.5) == "alta"
    assert classificar_prioridade(10.0) == "alta"


def test_r05_2_prioridade_media_de_6_5_a_7_4() -> None:
    assert classificar_prioridade(7.4) == "media"
    assert classificar_prioridade(6.5) == "media"


def test_r05_2_prioridade_baixa_abaixo_de_6_5() -> None:
    assert classificar_prioridade(6.4) == "baixa"
    assert classificar_prioridade(0.0) == "baixa"


def test_r05_2_sem_nota_fica_a_avaliar() -> None:
    assert classificar_prioridade(None) == "a avaliar"


def test_r05_2_nota_calculada_ja_traz_a_prioridade_da_faixa() -> None:
    assert calcular_nota(6.1, 0.97).prioridade == "alta"
    assert calcular_nota(6.9, None).prioridade == "media"
    assert calcular_nota(6.1, 0.0).prioridade == "baixa"
    assert calcular_nota(None, 0.97).prioridade == "a avaliar"


def test_r05_5_nota_da_biblioteca_e_a_maior_dos_achados() -> None:
    achados = [achado("GHSA-a", 6.1, 0.0), achado("GHSA-b", 6.1, 0.97), achado("GHSA-c", 6.9, None)]
    assert nota_da_biblioteca(achados) == 7.9


def test_r05_5_achado_sem_nota_nao_entra_na_nota_da_biblioteca() -> None:
    achados = [achado("GHSA-a", None, 0.97), achado("GHSA-b", 6.1, None)]
    assert nota_da_biblioteca(achados) == 6.1


def test_r05_5_biblioteca_so_com_achados_sem_nota_fica_sem_nota() -> None:
    assert nota_da_biblioteca([achado("GHSA-a", None, None)]) is None
    assert nota_da_biblioteca([]) is None


def test_r05_6_ordena_por_nota_decrescente() -> None:
    achados = [
        achado("GHSA-baixa", 6.1, 0.0),
        achado("GHSA-alta", 6.1, 0.97),
        achado("GHSA-media", 6.9, None),
    ]
    assert ghsas(ordenar_achados(achados)) == ["GHSA-alta", "GHSA-media", "GHSA-baixa"]


def test_r05_6_empate_na_nota_desfeito_pelo_cvss_decrescente() -> None:
    menor_cvss = achado("GHSA-menor-cvss", 6.0, 0.8)
    maior_cvss = achado("GHSA-maior-cvss", 8.0, 0.6)
    assert menor_cvss.nota.valor == maior_cvss.nota.valor == 7.0
    assert ghsas(ordenar_achados([menor_cvss, maior_cvss])) == [
        "GHSA-maior-cvss",
        "GHSA-menor-cvss",
    ]


def test_r05_6_achado_sem_nota_vai_para_o_fim_sem_sumir() -> None:
    achados = [achado("GHSA-sem-nota", None, 0.97), achado("GHSA-baixa", 2.0, 0.0)]
    assert ghsas(ordenar_achados(achados)) == ["GHSA-baixa", "GHSA-sem-nota"]


def test_r05_6_ordenar_nao_altera_a_lista_recebida() -> None:
    achados = [achado("GHSA-baixa", 6.1, 0.0), achado("GHSA-alta", 6.1, 0.97)]
    ordenar_achados(achados)
    assert ghsas(achados) == ["GHSA-baixa", "GHSA-alta"]
