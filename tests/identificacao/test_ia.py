import json
from typing import Any

from rastro.har.leitor import ler_har
from rastro.har.modelos import Requisicao
from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.identificacao.assinaturas import identificar_por_assinatura
from rastro.identificacao.ia import ETAPA, BibliotecasDaIA, identificar_em_bundles
from rastro.identificacao.modelos import Biblioteca, Evidencia
from rastro.travas.conferencia import conferir_bibliotecas
from tests.dubles import HAR_DO_JUICE_SHOP, TRECHO_DO_ANGULAR, ProvedorFalso, RegistroFalso

URL_DO_BUNDLE = "https://site/main.js"
TRECHO_DO_FONT_AWESOME = 'U$1=`FA "5.15.4"`'
GABARITO = HAR_DO_JUICE_SHOP.parent / "gabarito.json"


def bundle_com(meio: str, url: str = URL_DO_BUNDLE, indice: int = 3) -> Requisicao:
    enchimento = "a;" * (16 * 1024)
    return Requisicao(
        indice=indice,
        url=url,
        metodo="GET",
        status=200,
        tipo_conteudo="application/javascript",
        cabecalhos_resposta={},
        cookies_resposta=[],
        conteudo=enchimento + meio + enchimento,
    )


BUNDLE_DO_ANGULAR = bundle_com("function WC(e){let i=e?[`ng-version`,`22.2.2`]:uI(n)}")


def resposta(*bibliotecas: tuple[str, str, str]) -> str:
    lista = [{"pacote": p, "versao": v, "trecho": t} for p, v, t in bibliotecas]
    return json.dumps({"bibliotecas": lista}, ensure_ascii=False)


ANGULAR = ("@angular/core", "22.2.2", TRECHO_DO_ANGULAR)


def ia_que_responde(*respostas: str | FalhaDoProvedor) -> tuple[ClienteDeIA, ProvedorFalso]:
    fila: list[RespostaDoProvedor | FalhaDoProvedor] = []
    for item in respostas:
        if isinstance(item, FalhaDoProvedor):
            fila.append(item)
        else:
            fila.append(RespostaDoProvedor(item, tokens=None))
    provedor = ProvedorFalso(fila)
    return ClienteDeIA(provedor), provedor


def identificar(requisicoes: list[Requisicao], ia: ClienteDeIA | None) -> BibliotecasDaIA:
    return identificar_em_bundles(requisicoes, identificar_por_assinatura(requisicoes), ia)


def test_r03_1_sem_ia_nao_procura_em_bundles() -> None:
    assert identificar([BUNDLE_DO_ANGULAR], None) == BibliotecasDaIA([], [])


def test_r03_1_envia_a_ia_so_os_trechos_selecionados() -> None:
    ia, provedor = ia_que_responde(resposta())

    identificar([BUNDLE_DO_ANGULAR], ia)

    assert len(provedor.prompts) == 1
    assert TRECHO_DO_ANGULAR in provedor.prompts[0]
    assert "a;" * 200 not in provedor.prompts[0]
    assert [chamada.etapa for chamada in ia.chamadas] == [ETAPA]


def test_r03_1_bundle_sem_trecho_nao_chama_a_ia() -> None:
    ia, provedor = ia_que_responde()

    identificar([bundle_com("var a=1;")], ia)

    assert provedor.prompts == []


def test_r03_1_dado_sensivel_do_trecho_nao_vai_para_a_ia() -> None:
    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.c2lnbmF0dXJh"
    ia, provedor = ia_que_responde(resposta())

    identificar([bundle_com(f'var t="{token}",v="1.2.3";')], ia)

    assert token not in provedor.prompts[0]
    assert "[removido]" in provedor.prompts[0]


def test_r03_2_biblioteca_da_ia_tem_metodo_ia_e_o_trecho_como_evidencia() -> None:
    ia, _ = ia_que_responde(resposta(ANGULAR))

    resultado = identificar([BUNDLE_DO_ANGULAR], ia)

    assert resultado.bibliotecas == [
        Biblioteca(
            pacote="@angular/core",
            versao="22.2.2",
            metodo="ia",
            situacao="confirmada",
            conferida_no_npm=None,
            travas_que_falharam=[],
            evidencias=[Evidencia(3, URL_DO_BUNDLE, TRECHO_DO_ANGULAR)],
        )
    ]
    assert resultado.travas_acionadas == []


def test_r03_2_aceita_a_resposta_dentro_de_um_bloco_de_codigo() -> None:
    ia, _ = ia_que_responde("```json\n" + resposta(ANGULAR) + "\n```")

    resultado = identificar([BUNDLE_DO_ANGULAR], ia)

    assert [b.pacote for b in resultado.bibliotecas] == ["@angular/core"]


def test_r03_3_trecho_inventado_pela_ia_vai_para_a_confirmar() -> None:
    inventado = ("@angular/core", "22.2.2", "[`ng-versao`,`22.2.2`]")
    ia, _ = ia_que_responde(resposta(inventado))

    resultado = identificar([BUNDLE_DO_ANGULAR], ia)

    assert resultado.bibliotecas[0].situacao == "a_confirmar"
    assert resultado.bibliotecas[0].travas_que_falharam == ["trecho real"]
    assert [trava.trava for trava in resultado.travas_acionadas] == ["trecho real"]


def test_r03_3_versao_que_nao_esta_no_trecho_vai_para_a_confirmar() -> None:
    ia, _ = ia_que_responde(resposta(("@angular/core", "22.2.1", TRECHO_DO_ANGULAR)))

    resultado = identificar([BUNDLE_DO_ANGULAR], ia)

    assert resultado.bibliotecas[0].travas_que_falharam == ["ancoragem"]


def test_r03_3_biblioteca_barrada_antes_nao_e_consultada_no_npm() -> None:
    ia, _ = ia_que_responde(resposta(("@angular/core", "22.2.1", TRECHO_DO_ANGULAR)))
    registro = RegistroFalso()

    conferidas = conferir_bibliotecas(identificar([BUNDLE_DO_ANGULAR], ia).bibliotecas, registro)

    assert [b.versao for b in conferidas.a_confirmar] == ["22.2.1"]
    assert registro.consultas == []
    assert registro.leituras == []


def test_r03_3_biblioteca_da_ia_passa_pelo_npm_e_pelo_codigo_publicado() -> None:
    ia, _ = ia_que_responde(resposta(ANGULAR))
    registro = RegistroFalso()

    conferidas = conferir_bibliotecas(identificar([BUNDLE_DO_ANGULAR], ia).bibliotecas, registro)

    assert [(b.pacote, b.conferida_no_npm) for b in conferidas.confirmadas] == [
        ("@angular/core", True)
    ]
    assert registro.consultas == [("@angular/core", "22.2.2")]
    assert registro.leituras == [("@angular/core", "22.2.2")]


def test_r03_4_trecho_que_nao_esta_no_codigo_publicado_vai_para_a_confirmar() -> None:
    bundle = bundle_com('var U$1=`FA "5.15.4"`;')
    ia, _ = ia_que_responde(
        resposta(("@fortawesome/fontawesome-free", "5.15.4", TRECHO_DO_FONT_AWESOME))
    )

    conferidas = conferir_bibliotecas(identificar([bundle], ia).bibliotecas, RegistroFalso())

    assert conferidas.confirmadas == []
    assert conferidas.a_confirmar[0].travas_que_falharam == ["código confere"]
    assert {trava.trava for trava in conferidas.travas_acionadas} == {"código confere"}


def test_r03_5_falha_da_ia_segue_sem_bibliotecas_e_fica_no_painel() -> None:
    ia, _ = ia_que_responde(FalhaDoProvedor("tempo esgotado"))

    resultado = identificar([BUNDLE_DO_ANGULAR], ia)

    assert resultado == BibliotecasDaIA([], [])
    assert [(chamada.etapa, chamada.sucesso) for chamada in ia.chamadas] == [(ETAPA, False)]


def test_r03_5_resposta_fora_do_formato_e_descartada_e_registrada() -> None:
    ia, _ = ia_que_responde("Encontrei o Angular 22.2.2 no bundle.")

    resultado = identificar([BUNDLE_DO_ANGULAR], ia)

    assert resultado.bibliotecas == []
    assert [(t.trava, t.alvo) for t in resultado.travas_acionadas] == [
        ("formato fechado", "resposta da IA")
    ]


def test_r03_5_falha_num_bundle_nao_impede_os_outros() -> None:
    outro = bundle_com('var x="lib-x",v="1.0.0";', url="https://site/outro.js", indice=4)
    ia, _ = ia_que_responde(FalhaDoProvedor("sem resposta"), resposta(ANGULAR))

    resultado = identificar([outro, BUNDLE_DO_ANGULAR], ia)

    assert [b.pacote for b in resultado.bibliotecas] == ["@angular/core"]


def test_r21_8_ia_que_manda_cve_ou_cvss_tem_a_resposta_inteira_descartada() -> None:
    com_fatos = {"bibliotecas": [{"pacote": "@angular/core", "versao": "22.2.2",
                                  "trecho": TRECHO_DO_ANGULAR, "cve": "CVE-2025-0001",
                                  "cvss": "9.8"}]}
    ia, _ = ia_que_responde(json.dumps(com_fatos))

    resultado = identificar([BUNDLE_DO_ANGULAR], ia)

    assert resultado.bibliotecas == []
    assert "campo a mais" in resultado.travas_acionadas[0].motivo


def test_r03_2_mesma_biblioteca_em_dois_bundles_fica_uma_vez() -> None:
    copia = bundle_com("let i=e?[`ng-version`,`22.2.2`]:0;", url="https://site/b.js", indice=5)
    ia, _ = ia_que_responde(resposta(ANGULAR), resposta(ANGULAR))

    resultado = identificar([BUNDLE_DO_ANGULAR, copia], ia)

    assert [b.evidencias[0].indice_requisicao for b in resultado.bibliotecas] == [3]


def test_r03_4_em_dois_bundles_fica_a_biblioteca_que_passou_nas_travas() -> None:
    inventado = ("@angular/core", "22.2.2", "[`ng-versao`,`22.2.2`]")
    copia = bundle_com("let i=e?[`ng-version`,`22.2.2`]:0;", url="https://site/b.js", indice=5)
    ia, _ = ia_que_responde(resposta(inventado), resposta(ANGULAR))

    resultado = identificar([BUNDLE_DO_ANGULAR, copia], ia)

    assert [b.situacao for b in resultado.bibliotecas] == ["confirmada"]
    assert resultado.bibliotecas[0].evidencias[0].indice_requisicao == 5


def test_r03_2_biblioteca_ja_reconhecida_por_assinatura_nao_se_repete() -> None:
    jquery = ("jquery", "3.4.1", '"3.4.1"')
    por_assinatura = [
        Biblioteca("jquery", "3.4.1", "assinatura", "confirmada", None, [],
                   [Evidencia(1, "https://site/jquery.js", "/*! jQuery v3.4.1")])
    ]
    ia, _ = ia_que_responde(resposta(jquery))
    bundle = bundle_com('var jquery="3.4.1";')

    resultado = identificar_em_bundles([bundle], por_assinatura, ia)

    assert resultado.bibliotecas == []


def bibliotecas_do_gabarito(metodo_esperado: str) -> set[tuple[str, str]]:
    with GABARITO.open(encoding="utf-8") as arquivo:
        gabarito: dict[str, Any] = json.load(arquivo)
    juice_shop = next(alvo for alvo in gabarito["alvos"] if alvo["id"] == "juiceshop")
    return {
        (biblioteca["pacote"], biblioteca["versao"])
        for biblioteca in juice_shop["bibliotecas"]
        if biblioteca["metodo_esperado"] == metodo_esperado
    }


def test_r03_no_juice_shop_confirma_pela_ia_o_que_a_assinatura_nao_ve() -> None:
    requisicoes = ler_har(HAR_DO_JUICE_SHOP)
    font_awesome = ("@fortawesome/fontawesome-free", "5.15.4", TRECHO_DO_FONT_AWESOME)
    ia, provedor = ia_que_responde(resposta(ANGULAR), resposta(font_awesome))

    pela_ia = identificar(requisicoes, ia)
    conferidas = conferir_bibliotecas(pela_ia.bibliotecas, RegistroFalso())

    confirmadas = {(b.pacote, b.versao) for b in conferidas.confirmadas}
    assert identificar_por_assinatura(requisicoes) == []
    assert confirmadas == {("@angular/core", "22.2.2")}
    assert confirmadas <= bibliotecas_do_gabarito("ia")
    assert [(b.pacote, b.travas_que_falharam) for b in conferidas.a_confirmar] == [
        ("@fortawesome/fontawesome-free", ["código confere"])
    ]
    assert len(provedor.prompts) == 2
