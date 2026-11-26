from dataclasses import replace
from typing import Any

from rastro.fontes.conector import FonteSemResposta
from rastro.relatorio.limitacoes_da_analise import (
    TEXTO_BUNDLES_NAO_PROCURADOS,
    TEXTO_CONTINUA_IGUAL_SEM_IA,
)
from rastro.relatorio.montagem_do_relatorio import montar_relatorio
from tests.dubles import analise_da_loja, relatorio_da_loja


def ids_das_limitacoes(relatorio: dict[str, Any]) -> list[str]:
    return [limitacao["id"] for limitacao in relatorio["analise"]["limitacoes"]]


def test_r14_5_sem_ia_o_relatorio_marca_a_analise_como_incompleta() -> None:
    dados = relatorio_da_loja()["analise"]

    assert dados["ia"] is None
    assert ids_das_limitacoes(relatorio_da_loja()) == [
        "bundles_nao_procurados",
        "achados_sem_explicacao",
    ]
    assert dados["limitacoes"][0]["texto"] == TEXTO_BUNDLES_NAO_PROCURADOS
    assert dados["continua_igual"] == TEXTO_CONTINUA_IGUAL_SEM_IA


def test_r01_6_har_sem_javascript_avisa_no_relatorio() -> None:
    analise = replace(analise_da_loja(), tem_javascript=False)

    assert ids_das_limitacoes(montar_relatorio(analise))[-1] == "sem_javascript"


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
