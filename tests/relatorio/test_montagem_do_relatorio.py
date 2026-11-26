import json
from dataclasses import replace

from rastro.fluxo_da_analise import analisar
from rastro.pentest.modelos import ResultadoDoPentest, ResumoDoPentest
from rastro.relatorio.montagem_do_relatorio import VERSAO_DO_FORMATO, montar_relatorio
from tests.dubles import (
    HAR_DA_LOJA,
    ConectorFalso,
    NvdFalso,
    OsvFalso,
    RegistroFalso,
    analise_da_loja,
    relatorio_da_loja,
)


def test_r24_11_pentest_fica_separado_e_nao_muda_o_resumo() -> None:
    pentest = ResultadoDoPentest(
        versao_formato=2,
        origem="rastro",
        modo="ativo",
        executado_em="2026-11-20T12:00:00",
        har="loja.har",
        har_sha256="a" * 64,
        site="loja.exemplo.com",
        limite_de_requisicoes=20,
        requisicoes_enviadas=0,
        validacoes=[],
        resumo=ResumoDoPentest(0, 4, 0, 0, 0),
    )
    sem_pentest = relatorio_da_loja()
    com_pentest = montar_relatorio(analise_da_loja(), pentest)

    assert com_pentest["pentest"]["modo"] == "ativo"
    assert com_pentest["resumo"] == sem_pentest["resumo"]
    assert com_pentest["achados"] == sem_pentest["achados"]
    assert com_pentest["plano_de_acao"] == sem_pentest["plano_de_acao"]

    relatorio = relatorio_da_loja()

    assert relatorio["versao_formato"] == VERSAO_DO_FORMATO == 1
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
        "visita",
        "pentest",
    ]


def test_r13_7_relatorio_vira_json_sem_perder_nada() -> None:
    relatorio = relatorio_da_loja()

    assert json.loads(json.dumps(relatorio, ensure_ascii=False)) == relatorio


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


def test_r05_5_biblioteca_traz_pronta_a_prioridade_da_sua_nota() -> None:
    jquery, lodash = relatorio_da_loja()["bibliotecas"][:2]

    assert jquery["prioridade"] == "alta"
    assert lodash["achados"] == []
    assert lodash["prioridade"] is None


def test_r16_4_evidencias_saem_sem_os_valores_da_query_string() -> None:
    analise = analise_da_loja()
    jquery = analise.bibliotecas[0]
    com_token = replace(jquery.evidencias[0], url="https://loja.exemplo.com/a.js?token=segredo#x")
    checagem = next(checagem for checagem in analise.checagens if checagem.evidencia is not None)
    na_pagina = replace(checagem.evidencia, url="https://loja.exemplo.com/?code=segredo")
    analise = replace(
        analise,
        bibliotecas=[replace(jquery, evidencias=[com_token]), *analise.bibliotecas[1:]],
        checagens=[replace(checagem, evidencia=na_pagina)],
    )

    relatorio = montar_relatorio(analise)

    assert relatorio["bibliotecas"][0]["evidencias"][0]["url"] == (
        "https://loja.exemplo.com/a.js?[removido]"
    )
    assert relatorio["checagens"][0]["evidencia"]["url"] == "https://loja.exemplo.com/?[removido]"
    assert "segredo" not in json.dumps(relatorio)


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

    assert [biblioteca["id"] for biblioteca in relatorio["a_confirmar"]] == ["lodash@4.17.21"]
    assert relatorio["a_confirmar"][0]["travas_que_falharam"] == ["pacote existe"]
    assert [biblioteca["id"] for biblioteca in relatorio["bibliotecas"]] == ["jquery@3.4.1"]


def test_r14_5_sem_ia_bibliotecas_sem_explicacao() -> None:
    bibliotecas = relatorio_da_loja()["bibliotecas"]

    assert [biblioteca["explicacao"] for biblioteca in bibliotecas] == [None, None]


def test_r14_8_com_ia_o_relatorio_informa_o_provedor_e_conta_as_da_ia() -> None:
    analise = replace(analise_da_loja(), provedor_de_ia="kiro")
    relatorio = montar_relatorio(analise)

    assert relatorio["analise"]["ia"] == "kiro"
    assert relatorio["analise"]["limitacoes"] == []
    assert relatorio["analise"]["continua_igual"] is None
    assert relatorio["resumo"]["encontradas_so_pela_ia"] == 0


def test_r16_4_relatorio_nao_traz_valor_de_cookie_nem_token_do_har() -> None:
    texto = json.dumps(relatorio_da_loja(), ensure_ascii=False)

    assert "segredo-ficticio-da-sessao" not in texto
    assert "valor-ficticio-do-carrinho" not in texto
    assert "token-ficticio-de-teste" not in texto
    assert "Bearer" not in texto
    assert "sessao" in texto


def test_r08_5_plano_de_acao_vai_inteiro_na_ordem_com_o_texto_da_task() -> None:
    plano_de_acao = relatorio_da_loja()["plano_de_acao"]

    assert plano_de_acao[0]["id"] == "jquery@3.4.1"
    assert plano_de_acao[0]["texto_task"].startswith(
        "## [Rastro] Atualizar jquery de 3.4.1 para 3.5.0"
    )
    assert [acao["id"] for acao in plano_de_acao[1:]] == ["C01", "C02", "C06", "C04", "C05", "C08"]


def test_r04a_5_achado_leva_as_fontes_e_a_origem_de_cada_campo_para_o_json() -> None:
    osv, nvd = OsvFalso(), NvdFalso()
    analise = analisar(
        HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), conector_osv=osv, busca_de_cvss=nvd
    )

    aviso = montar_relatorio(analise)["achados"][0]["aviso"]

    assert aviso["fontes"] == ["GitHub Advisory", "OSV"]
    assert aviso["origem_dos_campos"]["versoes_afetadas"] == "GitHub Advisory"
    assert set(aviso["origem_dos_campos"]) == {
        "cve",
        "resumo",
        "cvss",
        "percentil_epss",
        "versoes_afetadas",
        "versao_corrigida",
        "link",
    }
