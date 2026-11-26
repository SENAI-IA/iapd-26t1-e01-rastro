import pytest

from rastro.fontes.modelos import Aviso
from rastro.travas.faixa_de_versao import descartar_fora_da_faixa
from rastro.travas.modelos import TravaAcionada


def aviso(ghsa: str, versoes_afetadas: str) -> Aviso:
    return Aviso(
        fontes=["GitHub Advisory"],
        apelidos=[],
        ghsa=ghsa,
        cve=None,
        resumo="Resumo do aviso",
        cvss=6.1,
        percentil_epss=None,
        versoes_afetadas=versoes_afetadas,
        versao_corrigida="3.5.0",
        link=f"https://github.com/advisories/{ghsa}",
    )


def test_r21_7_aviso_dentro_da_faixa_e_mantido_sem_registro() -> None:
    avisos = [aviso("GHSA-gxr4-xjj5-5px2", ">= 1.2, < 3.5.0")]

    mantidos, travas_acionadas = descartar_fora_da_faixa("jquery", "3.4.1", avisos)

    assert mantidos == avisos
    assert travas_acionadas == []


def test_r21_7_aviso_fora_da_faixa_e_descartado_e_registrado() -> None:
    dentro = aviso("GHSA-gxr4-xjj5-5px2", ">= 1.2, < 3.5.0")
    fora = aviso("GHSA-rmxg-73gg-4p98", "< 1.9.0")

    mantidos, travas_acionadas = descartar_fora_da_faixa("jquery", "3.4.1", [dentro, fora])

    assert mantidos == [dentro]
    assert travas_acionadas == [
        TravaAcionada(
            trava="faixa conferida",
            alvo="GHSA-rmxg-73gg-4p98 em jquery@3.4.1",
            motivo="a versão 3.4.1 está fora da faixa afetada `< 1.9.0`",
        )
    ]


def test_r21_7_escolhe_a_faixa_que_contem_a_versao_no_aviso_com_varias_faixas() -> None:
    primeira_faixa = aviso("GHSA-6c3j-c64m-qhgq", "< 1.0.3")
    segunda_faixa = aviso("GHSA-6c3j-c64m-qhgq", ">= 1.0.3, < 3.5.0")

    avisos = [primeira_faixa, segunda_faixa]

    mantidos, travas_acionadas = descartar_fora_da_faixa("jquery", "3.4.1", avisos)

    assert mantidos == [segunda_faixa]
    assert travas_acionadas == []


def test_r21_7_aviso_com_todas_as_faixas_fora_e_registrado_uma_vez() -> None:
    primeira_faixa = aviso("GHSA-6c3j-c64m-qhgq", "< 1.0.3")
    segunda_faixa = aviso("GHSA-6c3j-c64m-qhgq", ">= 1.0.3, < 3.4.0")

    mantidos, travas_acionadas = descartar_fora_da_faixa(
        "jquery", "3.4.1", [primeira_faixa, segunda_faixa]
    )

    assert mantidos == []
    assert travas_acionadas == [
        TravaAcionada(
            trava="faixa conferida",
            alvo="GHSA-6c3j-c64m-qhgq em jquery@3.4.1",
            motivo=(
                "a versão 3.4.1 está fora da faixa afetada `< 1.0.3`; "
                "a versão 3.4.1 está fora da faixa afetada `>= 1.0.3, < 3.4.0`"
            ),
        )
    ]


def test_r21_7_versao_inventada_fora_da_faixa_barra_o_aviso() -> None:
    avisos = [aviso("GHSA-gxr4-xjj5-5px2", ">= 1.2, < 3.5.0")]

    mantidos, travas_acionadas = descartar_fora_da_faixa("jquery", "3.7.1", avisos)

    assert mantidos == []
    motivo_esperado = "a versão 3.7.1 está fora da faixa afetada `>= 1.2, < 3.5.0`"
    assert travas_acionadas[0].motivo == motivo_esperado


@pytest.mark.parametrize("faixa", ["", ">= 1.2.0,", "~> 1.2", ">= latest", "< 1.2.3.4"])
def test_r21_7_faixa_ilegivel_descarta_o_aviso_e_diz_por_que(faixa: str) -> None:
    avisos = [aviso("GHSA-xxxx", faixa)]

    mantidos, travas_acionadas = descartar_fora_da_faixa("jquery", "3.4.1", avisos)

    assert mantidos == []
    assert travas_acionadas[0].motivo.startswith(f"não foi possível conferir a faixa `{faixa}`")


def test_r21_7_versao_ilegivel_descarta_o_aviso() -> None:
    avisos = [aviso("GHSA-gxr4-xjj5-5px2", ">= 1.2, < 3.5.0")]

    mantidos, travas_acionadas = descartar_fora_da_faixa("jquery", "versão nova", avisos)

    assert mantidos == []
    assert "versão nova" in travas_acionadas[0].motivo
