import pytest

from rastro.har.modelos import Requisicao
from rastro.identificacao.assinaturas import ASSINATURAS, identificar_pelo_nome_do_arquivo
from rastro.identificacao.modelos import Biblioteca, Evidencia


def script(url: str, indice: int = 0, tipo_conteudo: str | None = "text/javascript") -> Requisicao:
    return Requisicao(
        indice=indice,
        url=url,
        metodo="GET",
        status=200,
        tipo_conteudo=tipo_conteudo,
        cabecalhos_resposta={},
        cookies_resposta=[],
        conteudo=None,
    )


def pacotes_e_versoes(requisicoes: list[Requisicao]) -> list[tuple[str, str]]:
    bibliotecas = identificar_pelo_nome_do_arquivo(requisicoes)
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

    bibliotecas = identificar_pelo_nome_do_arquivo([script(url, indice=7)])

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

    bibliotecas = identificar_pelo_nome_do_arquivo(requisicoes)

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
