from rastro.fontes.consulta import AvisosDaBiblioteca
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.achados import calcular_risco
from tests.dubles import avisos_gravados_do_jquery

JQUERY = Biblioteca(
    pacote="jquery",
    versao="3.4.1",
    metodo="assinatura",
    situacao="confirmada",
    conferida_no_npm=None,
    travas_que_falharam=[],
    evidencias=[],
)


def test_r05_6_um_achado_por_aviso_em_ordem_de_nota_decrescente() -> None:
    avisos: list[AvisosDaBiblioteca] = [(JQUERY, avisos_gravados_do_jquery())]

    achados = calcular_risco(avisos)

    assert len(achados) == len(avisos_gravados_do_jquery())
    notas = [achado.nota.valor or 0.0 for achado in achados]
    assert notas == sorted(notas, reverse=True)
    assert all(achado.biblioteca == JQUERY for achado in achados)


def test_r05_1_sem_avisos_nao_ha_achado() -> None:
    assert calcular_risco([(JQUERY, [])]) == []
