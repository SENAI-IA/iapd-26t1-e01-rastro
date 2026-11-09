import json
from pathlib import Path

import pytest

from rastro.fluxo import analisar
from rastro.har.leitor import HarInvalido, HarNaoEncontrado
from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.relatorio.json import montar_relatorio
from tests.dubles import (
    DADOS,
    HAR_DA_LOJA,
    HAR_DO_JUICE_SHOP,
    TRECHO_DO_ANGULAR,
    ConectorFalso,
    ProvedorFalso,
    RegistroFalso,
)


def har_da_loja_sem_scripts(pasta: Path) -> Path:
    with HAR_DA_LOJA.open(encoding="utf-8") as arquivo:
        har = json.load(arquivo)
    har["log"]["entries"] = [har["log"]["entries"][0], har["log"]["entries"][3]]
    caminho = pasta / "sem-scripts.har"
    caminho.write_text(json.dumps(har), encoding="utf-8")
    return caminho


def test_analisar_segue_as_etapas_do_har_ao_plano() -> None:
    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso())

    assert analise.har == "loja.har"
    assert analise.site == "loja.exemplo.com"
    assert [(b.pacote, b.versao) for b in analise.bibliotecas] == [
        ("jquery", "3.4.1"),
        ("lodash", "4.17.21"),
    ]
    assert [achado.aviso.ghsa for achado in analise.achados] == [
        "GHSA-jpcq-cgw6-v4j6",
        "GHSA-gxr4-xjj5-5px2",
    ]
    assert [checagem.id for checagem in analise.checagens] == [
        "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08",
    ]
    assert analise.plano_de_acao[0].o_que_fazer == "Atualizar jquery de 3.4.1 para 3.5.0"
    assert analise.plano_de_acao[0].texto_task.startswith("## [Rastro] Atualizar jquery")


def test_r14_5_sem_ia_nao_ha_provedor_nem_explicacao() -> None:
    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso())

    assert analise.provedor_de_ia is None
    assert analise.explicacoes == {}
    assert all(acao.teste_verificacao is None for acao in analise.plano_de_acao)


def test_r14_8_com_ia_o_relatorio_informa_o_provedor_usado() -> None:
    ia = ClienteDeIA(ProvedorFalso([FalhaDoProvedor("sem resposta")], nome="claude"))

    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), ia)

    assert analise.provedor_de_ia == "claude"
    assert montar_relatorio(analise)["analise"]["ia"] == "claude"


EXPLICACAO_DO_JQUERY = {
    "o_que_e": "O jquery 3.4.1 tem falhas de XSS (GHSA-jpcq-cgw6-v4j6, GHSA-gxr4-xjj5-5px2).",
    "impacto": "Um atacante pode rodar código no navegador de quem acessa o site.",
    "como_corrigir": "Atualizar o jquery para a versão 3.5.0.",
    "teste_verificacao": "Abrir o site e conferir que o jquery carregado é o 3.5.0.",
}


def test_r07_1_com_ia_o_achado_e_explicado_e_o_teste_vai_para_a_task() -> None:
    resposta = RespostaDoProvedor(json.dumps(EXPLICACAO_DO_JQUERY, ensure_ascii=False), None)
    ia = ClienteDeIA(ProvedorFalso([resposta]))

    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), ia)

    explicacao = analise.explicacoes["jquery@3.4.1"]
    assert explicacao.gerada_por_ia is True
    assert analise.plano_de_acao[0].impacto == EXPLICACAO_DO_JQUERY["impacto"]
    assert "sugerido pela IA: confira antes de usar" in analise.plano_de_acao[0].texto_task
    assert [chamada.etapa for chamada in ia.chamadas] == ["explicar_achado"]


def test_r07_1_resposta_real_do_kiro_vira_explicacao_da_ia() -> None:
    gravada = (DADOS / "kiro-explicacao-jquery.txt").read_text(encoding="utf-8")
    ia = ClienteDeIA(ProvedorFalso([RespostaDoProvedor(gravada, None)], nome="kiro"))

    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), ia)

    assert analise.explicacoes["jquery@3.4.1"].gerada_por_ia is True
    assert analise.explicacoes["jquery@3.4.1"].como_corrigir.startswith("Atualizar o jQuery")
    assert [trava.trava for trava in analise.travas_acionadas] == ["faixa conferida"]


def test_r07_3_explicacao_barrada_entra_nas_travas_acionadas() -> None:
    inventada = {**EXPLICACAO_DO_JQUERY, "impacto": "Nota 9,8 no CVSS."}
    resposta = RespostaDoProvedor(json.dumps(inventada, ensure_ascii=False), None)
    ia = ClienteDeIA(ProvedorFalso([resposta]))

    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), ia)

    assert analise.explicacoes["jquery@3.4.1"].gerada_por_ia is False
    assert analise.plano_de_acao[0].teste_verificacao is None
    assert [trava.trava for trava in analise.travas_acionadas] == [
        "faixa conferida",
        "explicação sem fato novo",
    ]


def respostas_do_juice_shop() -> list[RespostaDoProvedor]:
    angular = {"pacote": "@angular/core", "versao": "22.2.2", "trecho": TRECHO_DO_ANGULAR}
    font_awesome = {
        "pacote": "@fortawesome/fontawesome-free",
        "versao": "5.15.4",
        "trecho": 'U$1=`FA "5.15.4"`',
    }
    return [
        RespostaDoProvedor(json.dumps({"bibliotecas": [angular]}), None),
        RespostaDoProvedor(json.dumps({"bibliotecas": [font_awesome]}), None),
    ]


def test_r03_3_biblioteca_da_ia_passa_pelas_travas_antes_do_relatorio() -> None:
    ia = ClienteDeIA(ProvedorFalso(respostas_do_juice_shop()))
    conector = ConectorFalso()

    analise = analisar(HAR_DO_JUICE_SHOP, conector, RegistroFalso(), ia)

    assert [(b.pacote, b.metodo) for b in analise.bibliotecas] == [("@angular/core", "ia")]
    assert [b.pacote for b in analise.a_confirmar] == ["@fortawesome/fontawesome-free"]
    assert conector.consultas == [("@angular/core", "22.2.2")]
    assert "código confere" in [trava.trava for trava in analise.travas_acionadas]
    assert [chamada.etapa for chamada in analise.chamadas_de_ia] == [
        "identificar_bibliotecas",
        "identificar_bibliotecas",
    ]
    assert montar_relatorio(analise)["resumo"]["encontradas_so_pela_ia"] == 1


def test_r21_7_aviso_fora_da_faixa_vira_trava_acionada() -> None:
    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso())

    assert [trava.trava for trava in analise.travas_acionadas] == ["faixa conferida"]
    assert analise.travas_acionadas[0].alvo == "GHSA-jpcq-cgw6-v4j6 em jquery@3.4.1"


def test_r21_4_pacote_nao_publicado_vai_para_a_confirmar_e_nao_e_consultado() -> None:
    fonte = ConectorFalso()
    analise = analisar(HAR_DA_LOJA, fonte, RegistroFalso(nao_publicados=frozenset({"jquery"})))

    assert [b.pacote for b in analise.a_confirmar] == ["jquery"]
    assert fonte.consultas == [("lodash", "4.17.21")]
    assert analise.achados == []
    assert analise.travas_acionadas[0].trava == "pacote existe"


def test_r04_3_falha_na_consulta_marca_a_biblioteca_e_segue() -> None:
    fonte = ConectorFalso(sem_resposta_para=frozenset({"jquery"}))
    analise = analisar(HAR_DA_LOJA, fonte, RegistroFalso())

    assert analise.nao_consultadas == {
        "jquery@3.4.1": "sem resposta do GitHub Advisory: tempo esgotado"
    }
    assert ("lodash", "4.17.21") in fonte.consultas
    assert analise.achados == []


def test_r16_1_so_consulta_fontes_por_pacote_e_versao_sem_tocar_o_site() -> None:
    fonte = ConectorFalso()
    registro = RegistroFalso()

    analisar(HAR_DA_LOJA, fonte, registro)

    assert fonte.consultas == [("jquery", "3.4.1"), ("lodash", "4.17.21")]
    assert registro.consultas == [("jquery", "3.4.1"), ("lodash", "4.17.21")]


def test_r01_6_har_sem_javascript_segue_com_as_checagens(tmp_path: Path) -> None:
    analise = analisar(har_da_loja_sem_scripts(tmp_path), ConectorFalso(), RegistroFalso())

    assert analise.tem_javascript is False
    assert analise.bibliotecas == []
    assert len(analise.checagens) == 8
    assert analise.plano_de_acao != []


def test_r01_5_analisar_nao_altera_o_har() -> None:
    antes = HAR_DA_LOJA.read_bytes()

    analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso())

    assert HAR_DA_LOJA.read_bytes() == antes


def test_r01_2_har_inexistente_para_antes_de_consultar(tmp_path: Path) -> None:
    fonte = ConectorFalso()

    with pytest.raises(HarNaoEncontrado):
        analisar(tmp_path / "nao-existe.har", fonte, RegistroFalso())

    assert fonte.consultas == []


def test_r01_3_har_invalido_para_a_analise() -> None:
    with pytest.raises(HarInvalido):
        analisar(DADOS / "har-invalido.har", ConectorFalso(), RegistroFalso())
