import json
from pathlib import Path
from typing import Any

import pytest

from rastro.har.leitor import ler_har
from rastro.har.modelos import Requisicao
from rastro.identificacao.assinaturas import (
    ASSINATURAS,
    algum_script_com_conteudo,
    identificar_por_assinatura,
)
from rastro.identificacao.modelos import Biblioteca, Evidencia

PASTA_DA_AVALIACAO = Path(__file__).resolve().parents[2] / "avaliacao"
AGREGADO_DO_DRUPAL = "http://127.0.0.1:8888/sites/default/files/js/js_agregado.js"
SCRIPT_QUALQUER = "https://loja.exemplo.com.br/js/vendor.js"


def script(
    url: str,
    indice: int = 0,
    tipo_conteudo: str | None = "text/javascript",
    conteudo: str | None = None,
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


def pacotes_e_versoes(requisicoes: list[Requisicao]) -> list[tuple[str, str]]:
    bibliotecas = identificar_por_assinatura(requisicoes)
    return [(biblioteca.pacote, biblioteca.versao) for biblioteca in bibliotecas]


def test_r02_1_reconhece_pela_url_do_arquivo() -> None:
    requisicoes = [script("https://loja.exemplo.com.br/js/jquery-3.4.1.min.js")]

    assert pacotes_e_versoes(requisicoes) == [("jquery", "3.4.1")]


def test_r02_1_reconhece_pela_url_de_cdn_com_arroba() -> None:
    requisicoes = [script("https://cdn.jsdelivr.net/npm/lodash@4.17.15/lodash.min.js")]

    assert pacotes_e_versoes(requisicoes) == [("lodash", "4.17.15")]


def test_r02_1_reconhece_pela_pasta_da_versao_na_cdn() -> None:
    requisicoes = [script("https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js")]

    assert pacotes_e_versoes(requisicoes) == [("jquery", "3.4.1")]


def test_r02_1_reconhece_a_versao_no_parametro_v() -> None:
    requisicoes = [script("http://127.0.0.1:8888/core/assets/vendor/ckeditor/ckeditor.js?v=4.10.1")]

    assert pacotes_e_versoes(requisicoes) == [("ckeditor", "4.10.1")]


def test_r02_1_reconhece_a_versao_no_parametro_ver() -> None:
    requisicoes = [script("https://blog.exemplo.com.br/wp-includes/js/jquery/jquery.min.js?ver=3.4.1")]

    assert pacotes_e_versoes(requisicoes) == [("jquery", "3.4.1")]


def test_r02_1_ignora_maiusculas_no_nome_do_arquivo() -> None:
    requisicoes = [script("https://loja.exemplo.com.br/js/jQuery-3.4.1.min.js")]

    assert pacotes_e_versoes(requisicoes) == [("jquery", "3.4.1")]


def test_r02_1_e_r02_5_registra_metodo_assinatura_e_a_url_como_evidencia() -> None:
    url = "https://loja.exemplo.com.br/js/jquery-3.4.1.min.js"

    bibliotecas = identificar_por_assinatura([script(url, indice=7)])

    assert bibliotecas == [
        Biblioteca(
            pacote="jquery",
            versao="3.4.1",
            metodo="assinatura",
            situacao="confirmada",
            conferida_no_npm=None,
            travas_que_falharam=[],
            evidencias=[Evidencia(indice_requisicao=7, url=url, trecho=None)],
        )
    ]


def test_r02_1_jquery_ui_nao_vira_jquery() -> None:
    requisicoes = [script("http://127.0.0.1:8080/WebGoat/js/libs/jquery-ui-1.10.4.js")]

    assert pacotes_e_versoes(requisicoes) == [("jquery-ui", "1.10.4")]


def test_r02_1_nome_dentro_de_outro_pacote_nao_conta() -> None:
    requisicoes = [
        script("https://cdn.jsdelivr.net/npm/react-bootstrap@1.0.0/dist/react-bootstrap.min.js"),
        script("https://cdn.jsdelivr.net/npm/moment-timezone@0.5.31/moment-timezone.min.js"),
    ]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_1_arquivo_sem_versao_no_nome_nao_e_reconhecido() -> None:
    requisicoes = [
        script("http://127.0.0.1:8080/WebGoat/js/libs/jquery.min.js"),
        script("http://127.0.0.1:8080/WebGoat/js/libs/underscore-min.js"),
    ]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_1_biblioteca_fora_da_tabela_nao_e_reconhecida() -> None:
    requisicoes = [script("http://127.0.0.1:8888/core/assets/vendor/modernizr/modernizr.min.js?v=3.3.1")]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_1_so_olha_scripts() -> None:
    requisicoes = [
        script("https://loja.exemplo.com.br/css/bootstrap-3.1.1.min.css", tipo_conteudo="text/css"),
        script("https://loja.exemplo.com.br/lib/bootstrap-3.1.1", tipo_conteudo=None),
    ]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_1_script_sem_extensao_conta_pelo_tipo_de_conteudo() -> None:
    requisicoes = [
        script("https://cdn.jsdelivr.net/npm/lodash@4.17.15/", tipo_conteudo="text/javascript")
    ]

    assert pacotes_e_versoes(requisicoes) == [("lodash", "4.17.15")]


def test_r02_1_nao_olha_o_host() -> None:
    requisicoes = [script("https://jquery-3.4.1.exemplo.com.br/app.js")]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_1_uma_biblioteca_por_requisicao_reconhecida() -> None:
    requisicoes = [
        script("https://loja.exemplo.com.br/js/jquery-3.4.1.min.js", indice=0),
        script("https://loja.exemplo.com.br/js/app.js", indice=1),
        script("https://loja.exemplo.com.br/js/bootstrap-3.1.1.min.js", indice=2),
    ]

    bibliotecas = identificar_por_assinatura(requisicoes)

    indices = [biblioteca.evidencias[0].indice_requisicao for biblioteca in bibliotecas]
    assert pacotes_e_versoes(requisicoes) == [("jquery", "3.4.1"), ("bootstrap", "3.1.1")]
    assert indices == [0, 2]


@pytest.mark.parametrize(
    ("url", "pacote", "versao"),
    [
        ("http://127.0.0.1:8080/WebGoat/js/libs/jquery-2.1.4.min.js", "jquery", "2.1.4"),
        ("https://code.jquery.com/ui/jquery-ui-1.12.1.min.js", "jquery-ui", "1.12.1"),
        ("https://cdn.jsdelivr.net/npm/bootstrap@3.1.1/dist/js/bootstrap.js", "bootstrap", "3.1.1"),
        ("https://cdn.jsdelivr.net/npm/lodash@4.17.15/lodash.min.js", "lodash", "4.17.15"),
        ("https://loja.exemplo.com.br/js/moment-2.29.1.min.js", "moment", "2.29.1"),
        ("https://cdn.jsdelivr.net/npm/angular@1.8.2/angular.min.js", "angular", "1.8.2"),
        ("https://loja.exemplo.com.br/js/underscore-1.10.2.min.js", "underscore", "1.10.2"),
        ("https://cdn.jsdelivr.net/npm/requirejs@2.3.6/require.js", "requirejs", "2.3.6"),
        ("http://127.0.0.1:8888/core/assets/vendor/ckeditor.js?v=4.10.1", "ckeditor", "4.10.1"),
    ],
    ids=[
        "jquery",
        "jquery-ui",
        "bootstrap",
        "lodash",
        "moment",
        "angular",
        "underscore",
        "requirejs",
        "ckeditor",
    ],
)
def test_r02_4_reconhece_cada_biblioteca_minima(url: str, pacote: str, versao: str) -> None:
    assert pacotes_e_versoes([script(url)]) == [(pacote, versao)]


def test_r02_4_tabela_tem_as_nove_bibliotecas_minimas() -> None:
    pacotes = {assinatura.pacote for assinatura in ASSINATURAS}

    assert pacotes == {
        "jquery",
        "jquery-ui",
        "bootstrap",
        "lodash",
        "moment",
        "angular",
        "underscore",
        "requirejs",
        "ckeditor",
    }


def evidencias_de(biblioteca: Biblioteca) -> list[tuple[int, str | None]]:
    return [(evidencia.indice_requisicao, evidencia.trecho) for evidencia in biblioteca.evidencias]


def test_r02_2_reconhece_pelo_comentario_e_guarda_o_trecho() -> None:
    url = "http://127.0.0.1:8080/WebGoat/js/libs/jquery.min.js"
    conteudo = "/*! jQuery v3.4.1 | (c) JS Foundation | jquery.org/license */\n!function(e,t){}"

    bibliotecas = identificar_por_assinatura([script(url, indice=16, conteudo=conteudo)])

    assert bibliotecas == [
        Biblioteca(
            pacote="jquery",
            versao="3.4.1",
            metodo="assinatura",
            situacao="confirmada",
            conferida_no_npm=None,
            travas_que_falharam=[],
            evidencias=[Evidencia(indice_requisicao=16, url=url, trecho="/*! jQuery v3.4.1")],
        )
    ]


@pytest.mark.parametrize(
    ("conteudo", "pacote", "versao"),
    [
        ("/*! jQuery v3.4.1 | (c) JS Foundation */", "jquery", "3.4.1"),
        ("/*!\n * jQuery JavaScript Library v1.11.0\n */", "jquery", "1.11.0"),
        ("/*! jQuery UI - v1.12.1 - 2016-09-14\n* http://jqueryui.com */", "jquery-ui", "1.12.1"),
        ("/*!\n * Bootstrap v3.1.1 (http://getbootstrap.com)\n */", "bootstrap", "3.1.1"),
        (
            "/**\n * @license\n * lodash 3.10.1 (Custom Build) lodash.com/license"
            " | Underscore.js 1.8.3 underscorejs.org/LICENSE\n */",
            "lodash",
            "3.10.1",
        ),
        ("//! moment.js\n//! version : 2.18.1\n//! license : MIT", "moment", "2.18.1"),
        ("/*\n AngularJS v1.8.2\n (c) 2010-2020 Google LLC.\n*/", "angular", "1.8.2"),
        ("/**\n * @license AngularJS v1.8.2\n */", "angular", "1.8.2"),
        ("(function(){\n//     Underscore.js 1.10.2\n", "underscore", "1.10.2"),
        ("/** vim: et:ts=4\n * @license RequireJS 2.3.6 Copyright", "requirejs", "2.3.6"),
    ],
    ids=[
        "jquery",
        "jquery-library",
        "jquery-ui",
        "bootstrap",
        "lodash-3",
        "moment",
        "angular-min",
        "angular",
        "underscore-depois-do-umd",
        "requirejs",
    ],
)
def test_r02_2_reconhece_o_comentario_de_cada_biblioteca(
    conteudo: str, pacote: str, versao: str
) -> None:
    requisicoes = [script(SCRIPT_QUALQUER, conteudo=conteudo)]

    assert pacotes_e_versoes(requisicoes) == [(pacote, versao)]


def test_r02_2_procura_o_comentario_no_conteudo_inteiro() -> None:
    conteudo = "var app = 1;\n" * 10000 + "/*! jQuery UI - v1.12.1 - 2017-03-31 */"
    requisicoes = [script(AGREGADO_DO_DRUPAL, conteudo=conteudo)]

    assert pacotes_e_versoes(requisicoes) == [("jquery-ui", "1.12.1")]


def test_r02_2_bundle_com_varios_comentarios_registra_cada_biblioteca() -> None:
    conteudo = (
        "/*! jQuery v3.2.1 | (c) JS Foundation */\n!function(){};\n"
        "//     Underscore.js 1.8.3\n(function(){});\n"
        "/*! jQuery UI - v1.12.1 - 2017-03-31 */\n(function(){});\n"
        "/*! jQuery UI - v1.12.1 - 2017-03-31 */\n(function(){});\n"
    )
    requisicoes = [script(AGREGADO_DO_DRUPAL, conteudo=conteudo)]

    assert pacotes_e_versoes(requisicoes) == [
        ("jquery", "3.2.1"),
        ("jquery-ui", "1.12.1"),
        ("underscore", "1.8.3"),
    ]


def test_r02_2_mencao_no_meio_do_comentario_nao_conta() -> None:
    conteudo = (
        "/*!\n * jQuery Form Plugin\n * version: 4.2.2\n * Requires jQuery v1.7.2 or later\n */\n"
        "/*!\n * jQuery Color Animations v2.1.2\n */\n"
        "// support: jQuery 1.6.1, 1.6.2\n"
        "var texto = 'jQuery v1.7.2';\n"
    )
    requisicoes = [script(AGREGADO_DO_DRUPAL, conteudo=conteudo)]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_2_cabecalho_do_lodash_nao_vira_underscore() -> None:
    conteudos = [
        "/**\n * @license\n * Lodash lodash.com/license | Underscore.js 1.8.3 underscorejs.org",
        "/**\n * @license\n * Lodash <https://lodash.com/>\n * Based on Underscore.js 1.8.3 <...>",
    ]
    requisicoes = [script(SCRIPT_QUALQUER, conteudo=conteudo) for conteudo in conteudos]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_2_nome_e_comentario_divergentes_vale_o_comentario() -> None:
    url = "http://127.0.0.1:8080/WebGoat/js/libs/jquery-ui-1.10.4.js"
    conteudo = "/*! jQuery UI - v1.10.3 - 2013-05-03\n* http://jqueryui.com */"

    bibliotecas = identificar_por_assinatura([script(url, indice=26, conteudo=conteudo)])

    assert [(biblioteca.pacote, biblioteca.versao) for biblioteca in bibliotecas] == [
        ("jquery-ui", "1.10.3")
    ]
    assert bibliotecas[0].evidencias == [
        Evidencia(indice_requisicao=26, url=url, trecho="/*! jQuery UI - v1.10.3")
    ]


def test_r02_2_nome_e_comentario_iguais_registram_uma_evidencia_com_o_trecho() -> None:
    url = "http://127.0.0.1:8080/WebGoat/js/libs/jquery-2.1.4.min.js"
    conteudo = "/*! jQuery v2.1.4 | (c) 2005, 2015 jQuery Foundation, Inc. */"

    bibliotecas = identificar_por_assinatura([script(url, indice=17, conteudo=conteudo)])

    assert len(bibliotecas) == 1
    assert evidencias_de(bibliotecas[0]) == [(17, "/*! jQuery v2.1.4")]


def test_r02_2_sem_comentario_vale_o_nome_do_arquivo() -> None:
    url = "http://127.0.0.1:8888/core/assets/vendor/ckeditor/ckeditor.js?v=4.10.1"
    conteudo = "/*\nCopyright (c) 2003-2018, CKSource - Frederico Knabben. All rights reserved.\n*/"

    bibliotecas = identificar_por_assinatura([script(url, conteudo=conteudo)])

    assert [(biblioteca.pacote, biblioteca.versao) for biblioteca in bibliotecas] == [
        ("ckeditor", "4.10.1")
    ]
    assert evidencias_de(bibliotecas[0]) == [(0, None)]


def test_r02_2_so_olha_o_conteudo_de_scripts() -> None:
    requisicoes = [
        script(
            "https://loja.exemplo.com.br/sobre.html",
            tipo_conteudo="text/html",
            conteudo="<script>/*! jQuery v3.4.1 */</script>",
        )
    ]

    assert pacotes_e_versoes(requisicoes) == []


def test_r02_3_mesma_biblioteca_em_duas_requisicoes_aparece_uma_vez() -> None:
    conteudo = "/*! jQuery v3.2.1 | (c) JS Foundation */\n!function(){};"
    requisicoes = [
        script("http://127.0.0.1:8888/files/js/js_um.js", indice=8, conteudo=conteudo),
        script("http://127.0.0.1:8888/files/js/js_dois.js", indice=39, conteudo=conteudo),
    ]

    bibliotecas = identificar_por_assinatura(requisicoes)

    assert len(bibliotecas) == 1
    assert evidencias_de(bibliotecas[0]) == [(8, "/*! jQuery v3.2.1"), (39, "/*! jQuery v3.2.1")]


def test_r02_3_mesma_biblioteca_pelo_nome_em_duas_requisicoes_aparece_uma_vez() -> None:
    url = "http://127.0.0.1:8888/core/assets/vendor/ckeditor/ckeditor.js?v=4.10.1"

    bibliotecas = identificar_por_assinatura([script(url, indice=64), script(url, indice=94)])

    assert len(bibliotecas) == 1
    assert evidencias_de(bibliotecas[0]) == [(64, None), (94, None)]


def test_r02_3_comentario_repetido_na_mesma_requisicao_vira_uma_evidencia() -> None:
    conteudo = "/*! jQuery UI - v1.12.1 */\n(function(){});\n" * 2
    requisicoes = [script(AGREGADO_DO_DRUPAL, indice=8, conteudo=conteudo)]

    bibliotecas = identificar_por_assinatura(requisicoes)

    assert evidencias_de(bibliotecas[0]) == [(8, "/*! jQuery UI - v1.12.1")]


def test_r02_3_versoes_diferentes_ficam_separadas() -> None:
    requisicoes = [
        script("http://127.0.0.1:8080/js/libs/jquery.min.js", conteudo="/*! jQuery v3.4.1 */"),
        script("http://127.0.0.1:8080/js/libs/jquery-2.min.js", conteudo="/*! jQuery v2.1.4 */"),
    ]

    assert pacotes_e_versoes(requisicoes) == [("jquery", "3.4.1"), ("jquery", "2.1.4")]


def bibliotecas_por_assinatura_no_gabarito(alvo: dict[str, Any]) -> set[tuple[str, str]]:
    esperadas = set()
    for biblioteca in alvo["bibliotecas"]:
        if biblioteca["metodo_esperado"] == "assinatura":
            esperadas.add((biblioteca["pacote"], biblioteca["versao"]))
    return esperadas


def alvos_do_gabarito() -> list[dict[str, Any]]:
    caminho = PASTA_DA_AVALIACAO / "gabarito.json"
    with caminho.open("r", encoding="utf-8") as arquivo:
        gabarito: dict[str, Any] = json.load(arquivo)
    alvos: list[dict[str, Any]] = gabarito["alvos"]
    return alvos


@pytest.mark.parametrize("alvo", alvos_do_gabarito(), ids=lambda alvo: alvo["id"])
def test_r02_2_e_r02_3_reconhece_nos_alvos_o_que_o_gabarito_espera(alvo: dict[str, Any]) -> None:
    requisicoes = ler_har(PASTA_DA_AVALIACAO / alvo["har"])

    bibliotecas = identificar_por_assinatura(requisicoes)

    reconhecidas = [(biblioteca.pacote, biblioteca.versao) for biblioteca in bibliotecas]
    assert len(reconhecidas) == len(set(reconhecidas))
    assert set(reconhecidas) == bibliotecas_por_assinatura_no_gabarito(alvo)


def test_r01_6_har_com_script_com_conteudo_tem_javascript() -> None:
    assert algum_script_com_conteudo([script(SCRIPT_QUALQUER, conteudo="var a = 1;")])


def test_r01_6_script_sem_conteudo_ou_conteudo_que_nao_e_script_nao_contam() -> None:
    sem_conteudo = script(SCRIPT_QUALQUER, conteudo=None)
    pagina = script("https://loja.exemplo.com.br/", tipo_conteudo="text/html", conteudo="<p>")

    assert not algum_script_com_conteudo([sem_conteudo, pagina])
