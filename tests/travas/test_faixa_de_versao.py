import pytest

from rastro.fontes.conector import Aviso
from rastro.travas.faixa_de_versao import descartar_fora_da_faixa, versao_na_faixa
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


def test_r21_7_faixa_com_inicio_e_fim_contem_a_versao_do_meio() -> None:
    assert versao_na_faixa("3.4.1", ">= 1.2.0, < 3.5.0")


def test_r21_7_faixa_com_fim_aberto_nao_contem_o_proprio_fim() -> None:
    assert not versao_na_faixa("3.5.0", ">= 1.2.0, < 3.5.0")


def test_r21_7_faixa_contem_o_proprio_inicio_fechado() -> None:
    assert versao_na_faixa("1.2.0", ">= 1.2.0, < 3.5.0")


def test_r21_7_versao_abaixo_do_inicio_fica_fora() -> None:
    assert not versao_na_faixa("1.1.9", ">= 1.2.0, < 3.5.0")


def test_r21_7_versao_com_dois_numeros_vale_com_zero_no_fim() -> None:
    assert versao_na_faixa("1.2.0", ">= 1.2, < 3.5.0")


@pytest.mark.parametrize(
    ("versao", "faixa", "esperado"),
    [
        ("2.1.0", "<= 2.1.0", True),
        ("2.1.1", "<= 2.1.0", False),
        ("1.0.2", "< 1.0.3", True),
        ("4.0.0", "> 3.9.9", True),
        ("3.9.9", "> 3.9.9", False),
        ("2.1.0", ">= 1.0.0, <= 2.1.0", True),
        ("2.1.0", "= 2.1.0", True),
        ("2.1.0", "2.1.0", True),
        ("2.1.1", "= 2.1.0", False),
        ("10.0.0", "< 9.0.0", False),
    ],
)
def test_r21_7_operadores_da_faixa(versao: str, faixa: str, esperado: bool) -> None:
    assert versao_na_faixa(versao, faixa) is esperado


def test_r21_7_pre_lancamento_e_menor_que_a_versao_final() -> None:
    assert versao_na_faixa("3.5.0-beta.1", ">= 1.2.0, < 3.5.0")


def test_r21_7_versao_final_nao_cabe_antes_do_pre_lancamento() -> None:
    assert not versao_na_faixa("3.5.0", "< 3.5.0-rc.1")


@pytest.mark.parametrize(
    ("menor", "maior"),
    [
        ("1.0.0-alpha", "1.0.0-alpha.1"),
        ("1.0.0-alpha.1", "1.0.0-beta"),
        ("1.0.0-beta.2", "1.0.0-beta.11"),
        ("1.0.0-rc.1", "1.0.0"),
    ],
)
def test_r21_7_pre_lancamentos_seguem_a_ordem_do_semver(menor: str, maior: str) -> None:
    assert versao_na_faixa(menor, f"< {maior}")
    assert not versao_na_faixa(maior, f"< {menor}")


def test_r21_7_metadado_de_build_nao_conta_na_comparacao() -> None:
    assert versao_na_faixa("3.4.1+build.7", "= 3.4.1")


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
