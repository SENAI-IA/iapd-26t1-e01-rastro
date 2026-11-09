import json
from pathlib import Path

import pytest

from rastro.fluxo import analisar
from rastro.har.leitor import HarInvalido, HarNaoEncontrado
from rastro.ia.cliente import ClienteDeIA
from rastro.relatorio.json import montar_relatorio
from tests.dubles import DADOS, HAR_DA_LOJA, ConectorFalso, ProvedorFalso, RegistroFalso


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
    ia = ClienteDeIA(ProvedorFalso(nome="claude"))

    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), ia)

    assert analise.provedor_de_ia == "claude"
    assert montar_relatorio(analise)["analise"]["ia"] == "claude"


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
