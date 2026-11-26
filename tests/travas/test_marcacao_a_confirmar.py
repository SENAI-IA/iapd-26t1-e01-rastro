from dataclasses import replace

from rastro.identificacao.modelos import Biblioteca
from rastro.travas.marcacao_a_confirmar import mandar_para_a_confirmar
from rastro.travas.modelos import TravaAcionada

CONFIRMADA = Biblioteca(
    pacote="jquery",
    versao="3.4.1",
    metodo="ia",
    situacao="confirmada",
    conferida_no_npm=True,
    travas_que_falharam=[],
    evidencias=[],
)


def acionada(trava: str) -> TravaAcionada:
    return TravaAcionada(trava, "jquery@3.4.1", "motivo")


def test_r21_10_biblioteca_barrada_vai_para_a_confirmar_com_o_nome_das_travas() -> None:
    barrada = mandar_para_a_confirmar(CONFIRMADA, [acionada("trecho real"), acionada("ancoragem")])

    assert barrada.situacao == "a_confirmar"
    assert barrada.travas_que_falharam == ["trecho real", "ancoragem"]


def test_r21_10_nome_da_trava_nao_se_repete() -> None:
    ja_barrada = replace(CONFIRMADA, travas_que_falharam=["ancoragem"])

    barrada = mandar_para_a_confirmar(ja_barrada, [acionada("ancoragem"), acionada("ancoragem")])

    assert barrada.travas_que_falharam == ["ancoragem"]
