from dataclasses import replace

from rastro.ia.cliente import ChamadaDaIA
from rastro.ia.provedor import FalhaDoProvedor, RespostaDoProvedor
from rastro.modelos_da_analise import Analise
from rastro.relatorio.montagem_do_relatorio import montar_relatorio
from tests.dubles import analise_da_loja, analise_da_loja_com_ia, relatorio_da_loja


def lodash_como_se_viesse_da_ia(analise: Analise) -> Analise:
    bibliotecas = [
        replace(biblioteca, metodo="ia") if biblioteca.pacote == "lodash" else biblioteca
        for biblioteca in analise.bibliotecas
    ]
    return replace(analise, bibliotecas=bibliotecas)


def chamada(tokens: int | None) -> ChamadaDaIA:
    return ChamadaDaIA("explicar_achado", "kiro", "entrada", "resposta", 1.2, tokens, True)


def test_r21_10_travas_acionadas_vao_para_o_painel_da_ia() -> None:
    ia = relatorio_da_loja()["ia"]

    assert ia["travas_acionadas"] == [
        {
            "trava": "faixa conferida",
            "alvo": "GHSA-rmxg-73gg-4p98 em jquery@3.4.1",
            "motivo": "a versão 3.4.1 está fora da faixa afetada `< 1.9.0`",
        }
    ]
    assert ia["chamadas"] == []
    assert ia["com_e_sem_ia"] is None
    assert ia["tokens_total"] is None


def test_r21_10_travas_barradas_com_ia_vao_para_o_painel_com_o_motivo() -> None:
    fora_do_formato = RespostaDoProvedor("Claro! Segue a explicação.", None)
    ia = montar_relatorio(analise_da_loja_com_ia(fora_do_formato))["ia"]

    assert [trava["trava"] for trava in ia["travas_acionadas"]] == [
        "faixa conferida",
        "formato fechado",
    ]
    barrada = ia["travas_acionadas"][1]
    assert barrada["alvo"] == "explicação de jquery@3.4.1"
    assert barrada["motivo"].startswith("explicação descartada:")


def test_r11_1_cada_chamada_vai_para_o_painel_com_entrada_resposta_tempo_e_tokens() -> None:
    relatorio = montar_relatorio(analise_da_loja_com_ia(RespostaDoProvedor("{}", 812)))
    chamadas = relatorio["ia"]["chamadas"]

    assert len(chamadas) == 1
    assert list(chamadas[0]) == [
        "etapa",
        "provedor",
        "entrada",
        "resposta",
        "duracao_s",
        "tokens",
        "sucesso",
    ]
    assert chamadas[0]["etapa"] == "explicar_achado"
    assert chamadas[0]["provedor"] == "kiro"
    assert "jquery" in chamadas[0]["entrada"]
    assert chamadas[0]["resposta"] == "{}"
    assert chamadas[0]["tokens"] == 812
    assert relatorio["ia"]["tokens_total"] == 812


def test_r11_1_chamada_que_falhou_vai_para_o_painel_com_o_motivo() -> None:
    relatorio = montar_relatorio(analise_da_loja_com_ia(FalhaDoProvedor("tempo limite")))
    chamada_que_falhou = relatorio["ia"]["chamadas"][0]

    assert chamada_que_falhou["sucesso"] is False
    assert chamada_que_falhou["resposta"] == "tempo limite"
    assert chamada_que_falhou["tokens"] is None


def test_r11_2_total_de_tokens_soma_as_chamadas() -> None:
    analise = replace(analise_da_loja(), provedor_de_ia="claude")
    analise = replace(analise, chamadas_de_ia=[chamada(1000), chamada(234)])

    assert montar_relatorio(analise)["ia"]["tokens_total"] == 1234


def test_r11_2_total_de_tokens_nao_informado_se_alguma_chamada_nao_informou() -> None:
    analise = replace(analise_da_loja(), provedor_de_ia="kiro")
    analise = replace(analise, chamadas_de_ia=[chamada(1000), chamada(None)])

    assert montar_relatorio(analise)["ia"]["tokens_total"] is None


def test_r11_2_com_ia_e_sem_chamadas_o_total_de_tokens_e_zero() -> None:
    analise = replace(analise_da_loja(), provedor_de_ia="kiro")

    assert montar_relatorio(analise)["ia"]["tokens_total"] == 0


def test_r11_3_com_ia_o_painel_compara_so_por_assinatura_e_com_ia() -> None:
    analise = replace(analise_da_loja(), provedor_de_ia="kiro")
    relatorio = montar_relatorio(lodash_como_se_viesse_da_ia(analise))

    assert relatorio["ia"]["com_e_sem_ia"] == {
        "bibliotecas": {"so_por_assinatura": 1, "com_ia": 2},
        "achados": {"so_por_assinatura": 2, "com_ia": 2},
    }
    assert relatorio["resumo"]["encontradas_so_pela_ia"] == 1


def test_r11_3_achado_de_biblioteca_da_ia_conta_so_com_ia() -> None:
    analise = replace(analise_da_loja(), provedor_de_ia="kiro")
    achados = [
        replace(achado, biblioteca=replace(achado.biblioteca, metodo="ia"))
        for achado in analise.achados
    ]
    relatorio = montar_relatorio(replace(analise, achados=achados))

    assert relatorio["ia"]["com_e_sem_ia"]["achados"] == {"so_por_assinatura": 0, "com_ia": 2}


def test_r11_3_sem_ia_o_painel_fica_sem_a_comparacao() -> None:
    assert relatorio_da_loja()["ia"]["com_e_sem_ia"] is None
