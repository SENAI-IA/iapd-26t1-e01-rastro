from dataclasses import replace

import pytest

from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.identificacao.modelos import Biblioteca, Evidencia
from rastro.travas.codigo_publicado import (
    conferir_codigo_publicado,
    string_esta_no_codigo,
    strings_do_trecho,
    trecho_prova_o_pacote,
)
from rastro.travas.modelos import TravaAcionada

URL_DO_BUNDLE = "https://juice-shop.local/main.js"
TRECHO_DO_ANGULAR = "[`ng-version`,`22.2.2`]"
CODIGOS_PUBLICADOS = {
    ("@angular/core", "22.2.2"): [
        "const NG_VERSION_ATTR_NAME = 'ng-version';",
        "const VERSION = new Version('22.2.2');",
    ],
    ("@angular/core", "22.2.1"): [
        "const NG_VERSION_ATTR_NAME = 'ng-version';",
        "const VERSION = new Version('22.2.1');",
    ],
    ("@angular/common", "22.2.2"): ["const VERSION = new Version('22.2.2');"],
    ("@fortawesome/fontawesome-free", "5.15.4"): ['var UNITS_PER_EM = "FA \\"5.15.4\\"";'],
}


class RegistroFalso:
    def __init__(self, motivo_sem_resposta: str | None = None) -> None:
        self.motivo_sem_resposta = motivo_sem_resposta
        self.leituras: list[tuple[str, str]] = []

    def existe(self, pacote: str, versao: str) -> bool:
        return (pacote, versao) in CODIGOS_PUBLICADOS

    def ler_codigo(self, pacote: str, versao: str) -> list[str]:
        self.leituras.append((pacote, versao))
        if self.motivo_sem_resposta is not None:
            raise ConsultaNaoRealizada(self.motivo_sem_resposta)
        return CODIGOS_PUBLICADOS[(pacote, versao)]


def sugerida_pela_ia(
    pacote: str = "@angular/core", versao: str = "22.2.2", trecho: str | None = TRECHO_DO_ANGULAR
) -> Biblioteca:
    return Biblioteca(
        pacote=pacote,
        versao=versao,
        metodo="ia",
        situacao="confirmada",
        conferida_no_npm=True,
        travas_que_falharam=[],
        evidencias=[Evidencia(indice_requisicao=3, url=URL_DO_BUNDLE, trecho=trecho)],
    )


def test_r21_5_trecho_real_do_pacote_passa() -> None:
    registro = RegistroFalso()

    biblioteca, travas_acionadas = conferir_codigo_publicado(sugerida_pela_ia(), registro)

    assert biblioteca == sugerida_pela_ia()
    assert travas_acionadas == []
    assert registro.leituras == [("@angular/core", "22.2.2")]


def test_r21_5_trecho_inventado_vai_para_a_confirmar() -> None:
    inventado = sugerida_pela_ia(trecho="[`ng-versao`,`22.2.2`]")

    biblioteca, travas_acionadas = conferir_codigo_publicado(inventado, RegistroFalso())

    assert biblioteca.situacao == "a_confirmar"
    assert biblioteca.travas_que_falharam == ["código confere"]
    assert travas_acionadas == [
        TravaAcionada(
            "código confere",
            "@angular/core@22.2.2",
            f"a string `ng-versao` do trecho de {URL_DO_BUNDLE} não aparece no código "
            "publicado de @angular/core@22.2.2",
        )
    ]


@pytest.mark.parametrize(
    ("pacote", "versao", "trecho"),
    [
        ("@angular/core", "22.2.1", TRECHO_DO_ANGULAR),
        ("@angular/common", "22.2.2", TRECHO_DO_ANGULAR),
        ("@angular/core", "22.2.2", "`22.2.2`"),
        ("@fortawesome/fontawesome-free", "5.15.4", 'U$1=`FA "5.15.4"`'),
    ],
    ids=["versao-vizinha", "pacote-irmao", "so-a-versao", "font-awesome-do-spike"],
)
def test_r21_5_casos_do_spike_que_a_trava_barra(pacote: str, versao: str, trecho: str) -> None:
    biblioteca, travas_acionadas = conferir_codigo_publicado(
        sugerida_pela_ia(pacote, versao, trecho), RegistroFalso()
    )

    assert biblioteca.situacao == "a_confirmar"
    assert [trava.trava for trava in travas_acionadas] == ["código confere"]


def test_r21_5_trecho_sem_prova_do_pacote_diz_o_motivo() -> None:
    _, travas_acionadas = conferir_codigo_publicado(
        sugerida_pela_ia(trecho="`22.2.2`"), RegistroFalso()
    )

    assert travas_acionadas[0].motivo == (
        f"o trecho de {URL_DO_BUNDLE} não tem a versão 22.2.2 "
        "e outra string que identifique o pacote"
    )


def test_r21_5_pacote_que_nao_pode_ser_lido_vai_para_a_confirmar() -> None:
    registro = RegistroFalso("pacote acima de 10 MB")

    biblioteca, travas_acionadas = conferir_codigo_publicado(sugerida_pela_ia(), registro)

    assert biblioteca.situacao == "a_confirmar"
    assert biblioteca.travas_que_falharam == ["código confere"]
    assert travas_acionadas == [
        TravaAcionada(
            "código confere",
            "@angular/core@22.2.2",
            "não foi possível ler o código publicado no npm: pacote acima de 10 MB",
        )
    ]


def test_r21_5_biblioteca_sem_trecho_vai_para_a_confirmar() -> None:
    sem_evidencia = replace(sugerida_pela_ia(), evidencias=[])

    biblioteca, travas_acionadas = conferir_codigo_publicado(sem_evidencia, RegistroFalso())
    com_trecho_nulo, _ = conferir_codigo_publicado(sugerida_pela_ia(trecho=None), RegistroFalso())

    assert biblioteca.situacao == "a_confirmar"
    assert travas_acionadas[0].motivo == "a IA não citou trecho"
    assert com_trecho_nulo.situacao == "a_confirmar"


def test_r21_5_trava_que_ja_falhou_nao_se_repete() -> None:
    ja_barrada = replace(
        sugerida_pela_ia(trecho="`22.2.2`"), travas_que_falharam=["código confere"]
    )

    biblioteca, _ = conferir_codigo_publicado(ja_barrada, RegistroFalso())

    assert biblioteca.travas_que_falharam == ["código confere"]


@pytest.mark.parametrize(
    ("trecho", "esperado"),
    [
        (TRECHO_DO_ANGULAR, ["ng-version", "22.2.2"]),
        ('U$1=`FA "5.15.4"`', ['FA "5.15.4"']),
        ('"FA \\"5.15.4\\""', ['FA "5.15.4"']),
        ("'it\\'s' + \"\"", ["it's"]),
        ('"\\x41\\u0042\\u{43}\\n\\q"', ["ABC\nq"]),
        ("sem aspas 22.2.2", []),
    ],
)
def test_r21_5_le_o_valor_das_strings_do_trecho(trecho: str, esperado: list[str]) -> None:
    assert strings_do_trecho(trecho) == esperado


@pytest.mark.parametrize(
    ("strings", "esperado"),
    [
        (["ng-version", "22.2.2"], True),
        (["Angular 22.2.2"], True),
        (["22.2.2"], False),
        (['FA "5.15.4"'], False),
        (["ng-version"], False),
        (["ng-version", "22.2.20"], False),
    ],
)
def test_r21_5_trecho_precisa_da_versao_e_de_algo_alem_dela(
    strings: list[str], esperado: bool
) -> None:
    versao = "5.15.4" if "FA" in strings[0] else "22.2.2"

    assert trecho_prova_o_pacote(strings, versao) is esperado


@pytest.mark.parametrize(
    ("valor", "codigo", "esperado"),
    [
        ('FA "5.15.4"', 'x = "FA \\"5.15.4\\"";', True),
        ('FA "5.15.4"', "x = 'FA \"5.15.4\"';", True),
        ('FA "5.15.4"', 'x = `FA "5.15.4"`;', True),
        ("ng-version", "setAttribute('ng-version', v)", True),
        ("ng-version", "// ng-version sem aspas", False),
        ("ng-version", "'ng-version-x'", False),
        ("linha\nnova", "'linha\\nnova'", True),
    ],
)
def test_r21_5_compara_o_valor_da_string_e_nao_a_forma_das_aspas(
    valor: str, codigo: str, esperado: bool
) -> None:
    assert string_esta_no_codigo(valor, [codigo]) is esperado
