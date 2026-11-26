from dataclasses import replace

from rastro.fontes.modelos import AvisosDaBiblioteca
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.achados import achados_da_biblioteca, calcular_risco
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
    avisos: list[AvisosDaBiblioteca] = [AvisosDaBiblioteca(JQUERY, avisos_gravados_do_jquery())]

    achados = calcular_risco(avisos)

    assert len(achados) == len(avisos_gravados_do_jquery())
    notas = [achado.nota.valor or 0.0 for achado in achados]
    assert notas == sorted(notas, reverse=True)
    assert all(achado.biblioteca == JQUERY for achado in achados)


def test_r05_1_sem_avisos_nao_ha_achado() -> None:
    assert calcular_risco([AvisosDaBiblioteca(JQUERY, [])]) == []


def test_achados_da_biblioteca_traz_so_os_do_pacote_e_versao_pedidos() -> None:
    outra_versao = replace(JQUERY, versao="3.5.0")
    achados = calcular_risco(
        [
            AvisosDaBiblioteca(JQUERY, avisos_gravados_do_jquery()),
            AvisosDaBiblioteca(outra_versao, avisos_gravados_do_jquery()),
        ]
    )

    da_biblioteca = achados_da_biblioteca("jquery@3.4.1", achados)

    assert len(da_biblioteca) == len(avisos_gravados_do_jquery())
    assert all(achado.biblioteca == JQUERY for achado in da_biblioteca)


def test_achados_da_biblioteca_sem_achados_devolve_lista_vazia() -> None:
    achados = calcular_risco([AvisosDaBiblioteca(JQUERY, avisos_gravados_do_jquery())])

    assert achados_da_biblioteca("lodash@4.17.21", achados) == []
