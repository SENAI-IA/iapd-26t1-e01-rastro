from dataclasses import replace

import pytest

from rastro.identificacao.modelos import Biblioteca, Evidencia
from rastro.travas.ancoragem import (
    conferir_ancoragem,
    trecho_foi_enviado,
    versao_esta_no_trecho,
)
from rastro.travas.modelos import TravaAcionada

URL_DO_BUNDLE = "https://juice-shop.local/main.js"
JANELA_ENVIADA = (
    "toLowerCase()}function WC(e,n,t,r,o){let i=e?[`ng-version`,`22.2.2`]:uI(n.selectors[0]),"
    "s=null,a=null,c=0;if(t)for(le"
)
TRECHO_DO_ANGULAR = "[`ng-version`,`22.2.2`]"


def sugerida_pela_ia(versao: str = "22.2.2", trecho: str | None = TRECHO_DO_ANGULAR) -> Biblioteca:
    return Biblioteca(
        pacote="@angular/core",
        versao=versao,
        metodo="ia",
        situacao="confirmada",
        conferida_no_npm=None,
        travas_que_falharam=[],
        evidencias=[Evidencia(indice_requisicao=3, url=URL_DO_BUNDLE, trecho=trecho)],
    )


def test_r21_2_trecho_copiado_do_que_foi_enviado_passa() -> None:
    biblioteca, travas_acionadas = conferir_ancoragem(sugerida_pela_ia(), [JANELA_ENVIADA])

    assert biblioteca == sugerida_pela_ia()
    assert travas_acionadas == []


def test_r21_2_trecho_inventado_vai_para_a_confirmar() -> None:
    inventado = "[`ng-versao`,`22.2.2`]"

    biblioteca, travas_acionadas = conferir_ancoragem(
        sugerida_pela_ia(trecho=inventado), [JANELA_ENVIADA]
    )

    assert biblioteca.situacao == "a_confirmar"
    assert biblioteca.travas_que_falharam == ["trecho real"]
    assert travas_acionadas == [
        TravaAcionada(
            "trecho real",
            "@angular/core@22.2.2",
            f"o trecho citado pela IA não está entre os trechos enviados de {URL_DO_BUNDLE}",
        )
    ]


@pytest.mark.parametrize(
    ("trecho", "enviados", "esperado"),
    [
        (TRECHO_DO_ANGULAR, [JANELA_ENVIADA], True),
        (TRECHO_DO_ANGULAR, ["/*! outro */", JANELA_ENVIADA], True),
        ("[`ng-version`, `22.2.2`]", [JANELA_ENVIADA], False),
        (TRECHO_DO_ANGULAR, [], False),
        ("", [JANELA_ENVIADA], False),
        ("   ", [JANELA_ENVIADA], False),
    ],
)
def test_r21_2_trecho_precisa_ser_copia_literal_de_um_enviado(
    trecho: str, enviados: list[str], esperado: bool
) -> None:
    assert trecho_foi_enviado(trecho, enviados) is esperado


def test_r21_2_biblioteca_sem_trecho_vai_para_a_confirmar() -> None:
    sem_trecho = sugerida_pela_ia(trecho=None)
    sem_evidencia = replace(sugerida_pela_ia(), evidencias=[])

    com_trecho_nulo, _ = conferir_ancoragem(sem_trecho, [JANELA_ENVIADA])
    sem_nada, travas_acionadas = conferir_ancoragem(sem_evidencia, [JANELA_ENVIADA])

    assert com_trecho_nulo.travas_que_falharam == ["trecho real", "ancoragem"]
    assert sem_nada.situacao == "a_confirmar"
    assert travas_acionadas[0].motivo == "a IA não citou trecho"


def test_r21_3_versao_fora_do_trecho_vai_para_a_confirmar() -> None:
    biblioteca, travas_acionadas = conferir_ancoragem(
        sugerida_pela_ia(versao="22.2.1"), [JANELA_ENVIADA]
    )

    assert biblioteca.situacao == "a_confirmar"
    assert biblioteca.travas_que_falharam == ["ancoragem"]
    assert travas_acionadas == [
        TravaAcionada(
            "ancoragem",
            "@angular/core@22.2.1",
            f"a versão 22.2.1 não aparece no trecho citado: procure `22.2.1` em {URL_DO_BUNDLE}",
        )
    ]


def test_r21_3_trecho_inventado_e_versao_ausente_registram_as_duas_travas() -> None:
    biblioteca, travas_acionadas = conferir_ancoragem(
        sugerida_pela_ia(versao="5.15.4", trecho="Angular 22"), [JANELA_ENVIADA]
    )

    assert biblioteca.travas_que_falharam == ["trecho real", "ancoragem"]
    assert [trava.trava for trava in travas_acionadas] == ["trecho real", "ancoragem"]


def test_r21_3_trava_que_ja_falhou_nao_se_repete() -> None:
    ja_barrada = replace(sugerida_pela_ia(versao="9.9.9"), travas_que_falharam=["ancoragem"])

    biblioteca, _ = conferir_ancoragem(ja_barrada, [JANELA_ENVIADA])

    assert biblioteca.travas_que_falharam == ["ancoragem"]


@pytest.mark.parametrize(
    ("versao", "trecho", "esperado"),
    [
        ("22.2.2", TRECHO_DO_ANGULAR, True),
        ("5.15.4", '`FA "5.15.4"`', True),
        ("3.4.1", "/*! jQuery v3.4.1 | (c) JS Foundation", True),
        ("1.0.0-rc.1", '"1.0.0-rc.1"', True),
        ("2.2.2", TRECHO_DO_ANGULAR, False),
        ("22.2", TRECHO_DO_ANGULAR, False),
        ("3.4.1", '"13.4.1"', False),
        ("3.4.1", '"3.4.10"', False),
        ("3.4.1", '"3.4.1.2"', False),
        ("1.0.0", '"1.0.0-rc.1"', False),
        ("3.4.1", "jquery 3-4-1", False),
    ],
)
def test_r21_3_versao_precisa_aparecer_inteira_no_trecho(
    versao: str, trecho: str, esperado: bool
) -> None:
    assert versao_esta_no_trecho(versao, trecho) is esperado
