from dataclasses import replace

from rastro.fontes.consulta import consultar_avisos
from rastro.identificacao.modelos import Biblioteca
from tests.dubles import ConectorFalso, OsvFalso

JQUERY = Biblioteca(
    pacote="jquery",
    versao="3.4.1",
    metodo="assinatura",
    situacao="confirmada",
    conferida_no_npm=None,
    travas_que_falharam=[],
    evidencias=[],
)
LODASH = replace(JQUERY, pacote="lodash", versao="4.17.21")


def test_r04_3_github_sem_resposta_marca_a_biblioteca_e_nao_consulta_o_osv() -> None:
    fonte = ConectorFalso(sem_resposta_para=frozenset({"jquery"}))
    osv = OsvFalso()

    consultados = consultar_avisos([JQUERY, LODASH], fonte, osv=osv)

    assert consultados.nao_consultadas == {
        "jquery@3.4.1": "sem resposta do GitHub Advisory: tempo esgotado"
    }
    assert [biblioteca.pacote for biblioteca, _ in consultados.avisos] == ["lodash"]
    assert osv.consultas == [("lodash", "4.17.21")]


def test_r04a_3_junta_os_avisos_do_github_e_do_osv_da_biblioteca() -> None:
    consultados = consultar_avisos([JQUERY], ConectorFalso(), osv=OsvFalso())

    _, avisos = consultados.avisos[0]
    assert any(aviso.fontes == ["GitHub Advisory", "OSV"] for aviso in avisos)
    assert consultados.fontes_sem_resposta == []

