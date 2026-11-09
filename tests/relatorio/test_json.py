import json
from dataclasses import replace
from typing import Any

from rastro.fluxo import Analise, analisar
from rastro.fontes.conector import FonteSemResposta
from rastro.ia.cliente import ChamadaIA, ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.relatorio.json import (
    TEXTO_BUNDLES_NAO_PROCURADOS,
    TEXTO_CONTINUA_IGUAL_SEM_IA,
    VERSAO_FORMATO,
    montar_relatorio,
)
from tests.dubles import (
    HAR_DA_LOJA,
    ConectorFalso,
    NvdFalso,
    OsvFalso,
    ProvedorFalso,
    RegistroFalso,
)


def analise_da_loja(fonte: ConectorFalso | None = None) -> Analise:
    return analisar(HAR_DA_LOJA, fonte or ConectorFalso(), RegistroFalso())


def relatorio_da_loja() -> dict[str, Any]:
    return montar_relatorio(analise_da_loja())


def analise_da_loja_com_ia(*respostas: RespostaDoProvedor | FalhaDoProvedor) -> Analise:
    ia = ClienteDeIA(ProvedorFalso(list(respostas), nome="kiro"))
    return analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), ia)


def lodash_como_se_viesse_da_ia(analise: Analise) -> Analise:
    bibliotecas = [
        replace(biblioteca, metodo="ia") if biblioteca.pacote == "lodash" else biblioteca
        for biblioteca in analise.bibliotecas
    ]
    return replace(analise, bibliotecas=bibliotecas)


def chamada(tokens: int | None) -> ChamadaIA:
    return ChamadaIA("explicar_achado", "kiro", "entrada", "resposta", 1.2, tokens, True)


def ids_das_limitacoes(relatorio: dict[str, Any]) -> list[str]:
    return [limitacao["id"] for limitacao in relatorio["analise"]["limitacoes"]]


def test_r13_7_relatorio_traz_versao_do_formato_e_todas_as_secoes() -> None:
    relatorio = relatorio_da_loja()

    assert relatorio["versao_formato"] == VERSAO_FORMATO == 1
    assert list(relatorio) == [
        "versao_formato",
        "analise",
        "resumo",
        "bibliotecas",
        "a_confirmar",
        "achados",
        "checagens",
        "plano_de_acao",
        "ia",
    ]


def test_r13_7_relatorio_vira_json_sem_perder_nada() -> None:
    relatorio = relatorio_da_loja()

    assert json.loads(json.dumps(relatorio, ensure_ascii=False)) == relatorio


def test_r13_7_resumo_traz_pronta_cada_contagem_da_tela() -> None:
    resumo = relatorio_da_loja()["resumo"]

    assert resumo == {
        "nota_maxima": 8.3,
        "acoes": 7,
        "acoes_por_prioridade": {"alta": 1, "media": 3, "baixa": 3, "a avaliar": 0},
        "bibliotecas": 2,
        "bibliotecas_vulneraveis": 1,
        "bibliotecas_a_confirmar": 0,
        "bibliotecas_nao_consultadas": 0,
        "achados": 2,
        "checagens_com_falha": 6,
        "checagens_nao_verificadas": 0,
        "encontradas_so_pela_ia": None,
    }


def test_r13_7_resumo_sem_achados_fica_sem_nota_maxima() -> None:
    fonte = ConectorFalso(sem_resposta_para=frozenset({"jquery"}))
    resumo = montar_relatorio(analise_da_loja(fonte))["resumo"]

    assert resumo["nota_maxima"] is None
    assert resumo["bibliotecas_vulneraveis"] == 0
    assert resumo["bibliotecas_nao_consultadas"] == 1


def test_r13_7_dados_da_analise() -> None:
    analise = analise_da_loja()
    dados = montar_relatorio(analise)["analise"]

    assert dados["har"] == "loja.har"
    assert dados["site"] == "loja.exemplo.com"
    assert dados["data"] == analise.inicio.isoformat(timespec="seconds")
    assert isinstance(dados["duracao_s"], float)


def test_r10_1_biblioteca_traz_origem_nota_e_achados() -> None:
    jquery = relatorio_da_loja()["bibliotecas"][0]

    assert jquery["id"] == "jquery@3.4.1"
    assert jquery["metodo"] == "assinatura"
    assert jquery["conferida_no_npm"] is True
    assert jquery["evidencias"] == [
        {
            "indice_requisicao": 1,
            "url": "https://loja.exemplo.com/js/jquery-3.4.1.min.js",
            "trecho": "/*! jQuery v3.4.1",
        }
    ]
    assert jquery["nota"] == 8.3
    assert jquery["achados"] == ["GHSA-jpcq-cgw6-v4j6", "GHSA-gxr4-xjj5-5px2"]
    assert jquery["motivo_nao_consultada"] is None


def test_r10_1_achado_traz_aviso_e_conta_da_nota() -> None:
    achado = relatorio_da_loja()["achados"][0]

    assert achado["biblioteca"] == "jquery@3.4.1"
    assert achado["aviso"]["ghsa"] == "GHSA-jpcq-cgw6-v4j6"
    assert achado["aviso"]["link"] == "https://github.com/advisories/GHSA-jpcq-cgw6-v4j6"
    assert achado["nota"]["conta"] == "10 × (0,5 × 6,9/10 + 0,5 × 0,97) = 8,3"


def test_r04_3_biblioteca_nao_consultada_traz_o_motivo() -> None:
    fonte = ConectorFalso(sem_resposta_para=frozenset({"jquery"}))
    jquery = montar_relatorio(analise_da_loja(fonte))["bibliotecas"][0]

    assert jquery["motivo_nao_consultada"] == "sem resposta do GitHub Advisory: tempo esgotado"
    assert jquery["nota"] is None


def test_r03_4_biblioteca_a_confirmar_fica_em_lista_propria() -> None:
    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(frozenset({"lodash"})))
    relatorio = montar_relatorio(analise)

    assert [b["id"] for b in relatorio["a_confirmar"]] == ["lodash@4.17.21"]
    assert relatorio["a_confirmar"][0]["travas_que_falharam"] == ["pacote existe"]
    assert [b["id"] for b in relatorio["bibliotecas"]] == ["jquery@3.4.1"]


def test_r14_5_sem_ia_o_relatorio_marca_a_analise_como_incompleta() -> None:
    dados = relatorio_da_loja()["analise"]

    assert dados["ia"] is None
    assert ids_das_limitacoes(relatorio_da_loja()) == [
        "bundles_nao_procurados",
        "achados_sem_explicacao",
    ]
    assert dados["limitacoes"][0]["texto"] == TEXTO_BUNDLES_NAO_PROCURADOS
    assert dados["continua_igual"] == TEXTO_CONTINUA_IGUAL_SEM_IA


def test_r14_5_sem_ia_bibliotecas_sem_explicacao() -> None:
    bibliotecas = relatorio_da_loja()["bibliotecas"]

    assert [biblioteca["explicacao"] for biblioteca in bibliotecas] == [None, None]


def test_r14_6_sem_ia_encontradas_so_pela_ia_e_nao_procurado_e_nao_zero() -> None:
    assert relatorio_da_loja()["resumo"]["encontradas_so_pela_ia"] is None


def test_r14_8_com_ia_o_relatorio_informa_o_provedor_e_conta_as_da_ia() -> None:
    analise = replace(analise_da_loja(), provedor_de_ia="kiro")
    relatorio = montar_relatorio(analise)

    assert relatorio["analise"]["ia"] == "kiro"
    assert relatorio["analise"]["limitacoes"] == []
    assert relatorio["analise"]["continua_igual"] is None
    assert relatorio["resumo"]["encontradas_so_pela_ia"] == 0


def test_r01_6_har_sem_javascript_avisa_no_relatorio() -> None:
    analise = replace(analise_da_loja(), tem_javascript=False)

    assert ids_das_limitacoes(montar_relatorio(analise))[-1] == "sem_javascript"


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


def test_r16_4_relatorio_nao_traz_valor_de_cookie_nem_token_do_har() -> None:
    texto = json.dumps(relatorio_da_loja(), ensure_ascii=False)

    assert "segredo-ficticio-da-sessao" not in texto
    assert "valor-ficticio-do-carrinho" not in texto
    assert "token-ficticio-de-teste" not in texto
    assert "Bearer" not in texto
    assert "sessao" in texto


def test_r08_plano_de_acao_vai_inteiro_com_o_texto_da_task() -> None:
    plano = relatorio_da_loja()["plano_de_acao"]

    assert plano[0]["id"] == "jquery@3.4.1"
    assert plano[0]["texto_task"].startswith("## [Rastro] Atualizar jquery de 3.4.1 para 3.5.0")
    assert [acao["id"] for acao in plano[1:]] == ["C01", "C02", "C06", "C04", "C05", "C08"]


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
        "etapa", "provedor", "entrada", "resposta", "duracao_s", "tokens", "sucesso",
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


def test_r04a_6_fonte_sem_resposta_vira_limitacao_com_o_alvo_e_o_motivo() -> None:
    sem_resposta = [
        FonteSemResposta("OSV", "jquery@3.4.1", "sem resposta do OSV: tempo esgotado"),
        FonteSemResposta("OSV", "lodash@4.17.21", "sem resposta do OSV: tempo esgotado"),
        FonteSemResposta("NVD", "CVE-2020-11022", "limite de consultas do NVD atingido (HTTP 403)"),
    ]
    analise = replace(analise_da_loja(), provedor_de_ia="kiro", fontes_sem_resposta=sem_resposta)

    limitacoes = montar_relatorio(analise)["analise"]["limitacoes"]

    assert [limitacao["id"] for limitacao in limitacoes] == [
        "fonte_sem_resposta_osv",
        "fonte_sem_resposta_nvd",
    ]
    assert limitacoes[0]["texto"] == (
        "O OSV não respondeu (jquery@3.4.1: sem resposta do OSV: tempo esgotado; "
        "lodash@4.17.21: sem resposta do OSV: tempo esgotado). "
        "Esses avisos vêm só do GitHub Advisory."
    )
    assert limitacoes[1]["texto"].endswith("Esses avisos seguem sem o CVSS do NVD.")


def test_r04a_5_achado_leva_as_fontes_e_a_origem_de_cada_campo_para_o_json() -> None:
    osv, nvd = OsvFalso(), NvdFalso()
    analise = analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), osv=osv, nvd=nvd)

    aviso = montar_relatorio(analise)["achados"][0]["aviso"]

    assert aviso["fontes"] == ["GitHub Advisory", "OSV"]
    assert aviso["origem_dos_campos"]["versoes_afetadas"] == "GitHub Advisory"
    assert set(aviso["origem_dos_campos"]) == {
        "cve", "resumo", "cvss", "percentil_epss", "versoes_afetadas", "versao_corrigida", "link",
    }
