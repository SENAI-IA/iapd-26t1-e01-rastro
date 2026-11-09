from rastro.har.leitor import ler_har
from rastro.har.modelos import Requisicao
from rastro.identificacao.assinaturas import identificar_por_assinatura
from rastro.identificacao.bundles import (
    MAXIMO_DE_TRECHOS_POR_BUNDLE,
    TAMANHO_DA_JANELA,
    escolher_bundles,
    extrair_trechos,
)
from tests.dubles import HAR_DO_JUICE_SHOP, TRECHO_DO_ANGULAR

ACIMA_DO_CORTE = 31 * 1024
ABAIXO_DO_CORTE = 29 * 1024


def script(
    url: str,
    conteudo: str | None,
    indice: int = 0,
    tipo_conteudo: str = "application/javascript",
) -> Requisicao:
    return Requisicao(
        indice=indice,
        url=url,
        metodo="GET",
        status=200,
        tipo_conteudo=tipo_conteudo,
        cabecalhos_resposta={},
        cookies_resposta=[],
        conteudo=conteudo,
    )


def codigo_com_tamanho(tamanho: int, meio: str = "") -> str:
    metade = (tamanho - len(meio)) // 2
    return "a;" * (metade // 2) + meio + "b;" * (metade // 2 + 1)


def nome_do_arquivo(url: str) -> str:
    return url.rsplit("/", 1)[1]


def urls_dos_bundles(requisicoes: list[Requisicao]) -> list[str]:
    bundles = escolher_bundles(requisicoes, identificar_por_assinatura(requisicoes))
    return [bundle.requisicao.url for bundle in bundles]


def test_r03_1_script_acima_de_30_kb_sem_assinatura_e_bundle() -> None:
    requisicoes = [
        script("https://site/main.js", codigo_com_tamanho(ACIMA_DO_CORTE), indice=0),
        script("https://site/pequeno.js", codigo_com_tamanho(ABAIXO_DO_CORTE), indice=1),
    ]

    assert urls_dos_bundles(requisicoes) == ["https://site/main.js"]


def test_r03_1_script_reconhecido_por_assinatura_nao_vai_para_a_ia() -> None:
    conteudo = "/*! jQuery v3.4.1 */" + codigo_com_tamanho(ACIMA_DO_CORTE)

    assert urls_dos_bundles([script("https://site/vendor.js", conteudo)]) == []


def test_r03_1_resposta_que_nao_e_script_ou_sem_conteudo_nao_e_bundle() -> None:
    requisicoes = [
        script("https://site/", codigo_com_tamanho(ACIMA_DO_CORTE), tipo_conteudo="text/html"),
        script("https://site/vazio.js", None, indice=1),
    ]

    assert urls_dos_bundles(requisicoes) == []


def test_r03_1_mesmo_bundle_baixado_duas_vezes_vai_uma_vez_so() -> None:
    conteudo = codigo_com_tamanho(ACIMA_DO_CORTE)
    requisicoes = [
        script("https://site/main.js", conteudo, indice=3),
        script("https://site/main.js", conteudo, indice=9),
    ]

    bundles = escolher_bundles(requisicoes, [])

    assert [bundle.requisicao.indice for bundle in bundles] == [3]


def test_r03_1_extrai_comentario_de_licenca_com_conteudo() -> None:
    conteudo = "/*!*/var a=1;/*! biblioteca-x v1.0.0 | MIT */var b=2;"

    assert extrair_trechos(conteudo) == ["/*! biblioteca-x v1.0.0 | MIT */"]


def test_r03_1_extrai_janela_de_300_caracteres_em_volta_da_versao_entre_aspas() -> None:
    conteudo = codigo_com_tamanho(2000, meio="[`ng-version`,`22.2.2`]")

    trechos = extrair_trechos(conteudo)

    assert len(trechos) == 1
    assert TRECHO_DO_ANGULAR in trechos[0]
    assert len(trechos[0]) == TAMANHO_DA_JANELA


def test_r03_1_versao_sem_aspas_e_palavra_version_nao_viram_trecho() -> None:
    conteudo = 'path d="M2.751 13.014 10.044 1.0.1";var x={version:0};this.version=40;'

    assert extrair_trechos(conteudo) == []


def test_r03_1_aceita_aspas_simples_duplas_crase_v_e_pre_lancamento() -> None:
    afastado = ";" * TAMANHO_DA_JANELA
    versoes = ["'1.2.3'", '"v4.5.6"', "`7.8.9-rc.1`"]

    trechos = extrair_trechos(afastado.join(versoes))

    assert len(trechos) == len(versoes)
    for versao, trecho in zip(versoes, trechos, strict=True):
        assert versao in trecho


def test_r03_1_versoes_proximas_ficam_na_mesma_janela() -> None:
    conteudo = 'var a="1.2.3",b="4.5.6";'

    assert extrair_trechos(conteudo) == [conteudo]


def test_r03_1_no_maximo_5_trechos_por_bundle_comecando_pelas_licencas() -> None:
    afastado = ";" * TAMANHO_DA_JANELA
    licencas = "".join(f"/*! lib-{numero} */" for numero in range(3))
    versoes = afastado.join(f'"{numero}.0.0"' for numero in range(5))

    trechos = extrair_trechos(licencas + afastado + versoes)

    assert len(trechos) == MAXIMO_DE_TRECHOS_POR_BUNDLE
    assert trechos[:3] == ["/*! lib-0 */", "/*! lib-1 */", "/*! lib-2 */"]


def test_r03_1_comentario_de_licenca_longo_e_cortado_na_janela() -> None:
    conteudo = "/*! " + "x" * 1000 + " */"

    assert len(extrair_trechos(conteudo)[0]) == TAMANHO_DA_JANELA


def test_r03_1_no_juice_shop_o_trecho_do_angular_vai_para_a_ia() -> None:
    requisicoes = ler_har(HAR_DO_JUICE_SHOP)

    bundles = escolher_bundles(requisicoes, identificar_por_assinatura(requisicoes))

    trechos_por_script = {nome_do_arquivo(b.requisicao.url): b.trechos for b in bundles}
    assert sorted(trechos_por_script) == [
        "chunk-1qQQGal7.js", "chunk-Cv2YgWUq.js", "main.js", "polyfills.js",
    ]
    assert TRECHO_DO_ANGULAR in trechos_por_script["chunk-Cv2YgWUq.js"][0]
    assert 'U$1=`FA "5.15.4"`' in trechos_por_script["main.js"][0]
    assert trechos_por_script["polyfills.js"] == []
