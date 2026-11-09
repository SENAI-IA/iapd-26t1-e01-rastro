import json
from pathlib import Path

import pytest

from rastro.acao.plano import CORRECOES_DAS_CHECAGENS, montar_plano_de_acao
from rastro.configuracao import checagens as regras
from rastro.configuracao.modelos import Checagem, RegraDeChecagem, SituacaoDaChecagem
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.conector import Aviso
from rastro.fontes.github_advisory import converter_resposta
from rastro.identificacao.modelos import Biblioteca, SituacaoDaBiblioteca
from rastro.risco.modelos import Achado
from rastro.risco.nota import calcular_nota
from rastro.travas.faixa_de_versao import descartar_fora_da_faixa

DADOS = Path(__file__).parent.parent / "dados"


def biblioteca(
    pacote: str, versao: str, situacao: SituacaoDaBiblioteca = "confirmada"
) -> Biblioteca:
    return Biblioteca(
        pacote=pacote,
        versao=versao,
        metodo="assinatura",
        situacao=situacao,
        conferida_no_npm=None,
        travas_que_falharam=[],
        evidencias=[],
    )


def achado(
    da_biblioteca: Biblioteca,
    ghsa: str,
    versao_corrigida: str | None,
    cvss: float | None = 6.1,
    percentil_epss: float | None = 0.5,
    resumo: str = "Resumo do aviso",
) -> Achado:
    aviso = Aviso(
        fontes=["GitHub Advisory"],
        apelidos=[],
        ghsa=ghsa,
        cve=None,
        resumo=resumo,
        cvss=cvss,
        percentil_epss=percentil_epss,
        versoes_afetadas="< 99.0.0",
        versao_corrigida=versao_corrigida,
        link=f"https://github.com/advisories/{ghsa}",
    )
    return Achado(da_biblioteca, aviso, calcular_nota(cvss, percentil_epss))


def checagem(regra: RegraDeChecagem, situacao: SituacaoDaChecagem = "falhou") -> Checagem:
    return Checagem(
        id=regra.id,
        titulo=regra.titulo,
        situacao=situacao,
        severidade=regra.severidade,
        quem_resolve=regra.quem_resolve,
        evidencia=None,
        detalhe="a página não envia o cabeçalho: https://loja.exemplo.com/",
    )


def achados_reais_do_jquery() -> list[Achado]:
    jquery = biblioteca("jquery", "3.4.1")
    resposta = json.loads((DADOS / "advisory-jquery-3.4.1.json").read_text(encoding="utf-8"))
    avisos, _ = descartar_fora_da_faixa("jquery", "3.4.1", converter_resposta(resposta, "jquery"))
    return [
        Achado(jquery, aviso, calcular_nota(aviso.cvss, aviso.percentil_epss)) for aviso in avisos
    ]


JQUERY = biblioteca("jquery", "3.4.1")
LODASH = biblioteca("lodash", "4.17.15")


def test_r08_1_uma_acao_por_biblioteca_com_os_avisos_reais_do_jquery() -> None:
    plano = montar_plano_de_acao(achados_reais_do_jquery(), {}, [])

    assert len(plano) == 1
    acao = plano[0]
    assert acao.id == "jquery@3.4.1"
    assert acao.o_que_fazer == "Atualizar jquery de 3.4.1 para 3.5.0"
    assert acao.refs == ["GHSA-jpcq-cgw6-v4j6", "GHSA-gxr4-xjj5-5px2"]
    assert acao.nota == 8.3
    assert acao.prioridade == "alta"


def test_r08_1_versao_alvo_e_a_maior_versao_corrigida_dos_avisos() -> None:
    achados = [
        achado(LODASH, "GHSA-a", "4.17.16"),
        achado(LODASH, "GHSA-b", "4.17.21"),
        achado(LODASH, "GHSA-c", "4.17.19"),
    ]

    acao = montar_plano_de_acao(achados, {}, [])[0]

    assert acao.o_que_fazer == "Atualizar lodash de 4.17.15 para 4.17.21"


def test_r08_1_versao_alvo_compara_numero_e_nao_texto() -> None:
    achados = [achado(LODASH, "GHSA-a", "4.17.9"), achado(LODASH, "GHSA-b", "4.17.10")]

    acao = montar_plano_de_acao(achados, {}, [])[0]

    assert acao.o_que_fazer.endswith("para 4.17.10")


def test_r08_1_versao_alvo_final_vem_depois_do_pre_lancamento() -> None:
    achados = [achado(JQUERY, "GHSA-a", "3.5.0-rc.1"), achado(JQUERY, "GHSA-b", "3.5.0")]

    acao = montar_plano_de_acao(achados, {}, [])[0]

    assert acao.o_que_fazer.endswith("para 3.5.0")


def test_r08_1_cada_biblioteca_e_cada_versao_tem_a_sua_acao() -> None:
    jquery_antigo = biblioteca("jquery", "1.12.4")
    achados = [
        achado(JQUERY, "GHSA-a", "3.5.0"),
        achado(LODASH, "GHSA-b", "4.17.21"),
        achado(jquery_antigo, "GHSA-c", "3.0.0"),
        achado(JQUERY, "GHSA-d", "3.5.0"),
    ]

    plano = montar_plano_de_acao(achados, {}, [])

    assert sorted(acao.id for acao in plano) == ["jquery@1.12.4", "jquery@3.4.1", "lodash@4.17.15"]


def test_r08_1_biblioteca_a_confirmar_fica_fora_do_plano() -> None:
    a_confirmar = biblioteca("moment", "2.18.1", situacao="a_confirmar")

    plano = montar_plano_de_acao([achado(a_confirmar, "GHSA-a", "2.29.4")], {}, [])

    assert plano == []


def test_r08_2_uma_acao_por_checagem_com_falha() -> None:
    checagens = [
        checagem(regras.CSP_AUSENTE),
        checagem(regras.HSTS_AUSENTE, "passou"),
        checagem(regras.COOKIE_SEM_HTTPONLY, "nao_verificada"),
        checagem(regras.SERVIDOR_EXPOE_VERSAO),
    ]

    plano = montar_plano_de_acao([], {}, checagens)

    assert [acao.id for acao in plano] == ["C01", "C05"]
    assert plano[0].refs == ["C01"]


@pytest.mark.parametrize(
    "regra",
    [
        regras.CSP_AUSENTE,
        regras.HSTS_AUSENTE,
        regras.NOSNIFF_AUSENTE,
        regras.FRAME_SEM_PROTECAO,
        regras.SERVIDOR_EXPOE_VERSAO,
        regras.COOKIE_SEM_HTTPONLY,
        regras.COOKIE_SEM_SECURE,
        regras.COOKIE_SEM_SAMESITE,
    ],
)
def test_r08_2_toda_checagem_tem_o_que_fazer_e_impacto(regra: RegraDeChecagem) -> None:
    acao = montar_plano_de_acao([], {}, [checagem(regra)])[0]

    assert acao.o_que_fazer == CORRECOES_DAS_CHECAGENS[regra.id].o_que_fazer
    assert acao.impacto == CORRECOES_DAS_CHECAGENS[regra.id].impacto
    assert acao.prioridade == regra.severidade
    assert acao.quem_resolve == regra.quem_resolve
    assert acao.nota is None


def test_r08_3_acao_da_biblioteca_traz_porque_impacto_e_quem_resolve() -> None:
    achados = [
        achado(
            JQUERY, "GHSA-a", "3.5.0", cvss=6.1, percentil_epss=0.97, resumo="XSS no htmlPrefilter"
        ),
        achado(JQUERY, "GHSA-b", "3.5.0", cvss=6.1, percentil_epss=0.2, resumo="Outro XSS"),
    ]

    acao = montar_plano_de_acao(achados, {}, [])[0]

    assert acao.porque == "2 falhas conhecidas (GHSA-a, GHSA-b). Nota 7,9 (alta)."
    assert acao.impacto == "XSS no htmlPrefilter"
    assert acao.quem_resolve == "dev front-end"


def test_r08_3_impacto_vem_da_explicacao_quando_existe() -> None:
    explicacao = Explicacao(
        o_que_e="Falha de XSS",
        impacto="Texto do usuário pode virar script na página.",
        como_corrigir="Atualizar o pacote",
        teste_verificacao="Abrir a página com um texto de teste",
        gerada_por_ia=True,
    )

    acao = montar_plano_de_acao(
        [achado(JQUERY, "GHSA-a", "3.5.0")], {"jquery@3.4.1": explicacao}, []
    )[0]

    assert acao.impacto == "Texto do usuário pode virar script na página."


def test_r08_3_biblioteca_sem_cvss_fica_sem_nota_e_a_avaliar() -> None:
    acao = montar_plano_de_acao(
        [achado(JQUERY, "GHSA-a", "3.5.0", cvss=None, percentil_epss=None)], {}, []
    )[0]

    assert acao.nota is None
    assert acao.prioridade == "a avaliar"
    assert acao.porque == "1 falha conhecida (GHSA-a). Sem nota, falta CVSS (a avaliar)."


def test_r08_3_acao_da_checagem_traz_a_regra_e_a_severidade_no_porque() -> None:
    acao = montar_plano_de_acao([], {}, [checagem(regras.CSP_AUSENTE)])[0]

    assert acao.porque == (
        "Regra C01 (CSP ausente), severidade média: "
        "a página não envia o cabeçalho: https://loja.exemplo.com/"
    )


def test_r08_4_sem_versao_corrigida_avisa_sem_correcao_publicada() -> None:
    acao = montar_plano_de_acao([achado(JQUERY, "GHSA-a", None)], {}, [])[0]

    assert acao.o_que_fazer == "jquery 3.4.1 sem correção publicada: avaliar troca ou mitigação"


def test_r08_4_um_aviso_sem_correcao_entre_outros_com_correcao() -> None:
    achados = [achado(JQUERY, "GHSA-a", "3.5.0"), achado(JQUERY, "GHSA-b", None)]

    acao = montar_plano_de_acao(achados, {}, [])[0]

    assert acao.o_que_fazer == (
        "Atualizar jquery de 3.4.1 para 3.5.0; "
        "GHSA-b sem correção publicada: avaliar troca ou mitigação"
    )


def test_r08_5_ordena_por_prioridade_e_dentro_dela_por_nota_decrescente() -> None:
    bootstrap = biblioteca("bootstrap", "3.3.7")
    angular = biblioteca("angular", "1.5.0")
    achados = [
        achado(LODASH, "GHSA-baixa", "4.17.21", cvss=5.0, percentil_epss=0.1),
        achado(bootstrap, "GHSA-sem-nota", "3.4.1", cvss=None, percentil_epss=None),
        achado(JQUERY, "GHSA-alta-menor", "3.5.0", cvss=6.1, percentil_epss=0.9),
        achado(angular, "GHSA-alta-maior", "1.8.0", cvss=9.8, percentil_epss=0.9),
    ]
    checagens = [checagem(regras.NOSNIFF_AUSENTE), checagem(regras.CSP_AUSENTE)]

    plano = montar_plano_de_acao(achados, {}, checagens)

    assert [acao.id for acao in plano] == [
        "angular@1.5.0",
        "jquery@3.4.1",
        "C01",
        "lodash@4.17.15",
        "C03",
        "bootstrap@3.3.7",
    ]


def test_r08_5_nota_da_biblioteca_e_a_maior_dos_seus_achados() -> None:
    achados = [
        achado(JQUERY, "GHSA-a", "3.5.0", cvss=5.0, percentil_epss=0.1),
        achado(JQUERY, "GHSA-b", "3.5.0", cvss=9.8, percentil_epss=0.9),
    ]

    acao = montar_plano_de_acao(achados, {}, [])[0]

    assert acao.nota == 9.4
    assert acao.refs == ["GHSA-b", "GHSA-a"]
