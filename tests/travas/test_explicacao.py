import json

import pytest

from rastro.travas.explicacao import conferir_explicacao
from rastro.travas.modelos import TravaAcionada

ENTRADA_DO_JQUERY = json.dumps(
    {
        "pacote": "jquery",
        "versao": "3.4.1",
        "url": "https://loja.exemplo.com.br/js/jquery-3.4.1.min.js",
        "avisos": [
            {
                "ghsa": "GHSA-gxr4-xjj5-5px2",
                "cve": "CVE-2020-11022",
                "resumo": "Potential XSS vulnerability in jQuery",
                "versoes_afetadas": ">= 1.2, < 3.5.0",
                "versao_corrigida": "3.5.0",
            }
        ],
    },
    ensure_ascii=False,
)


def explicacao(**mudancas: str) -> dict[str, str]:
    return {
        "o_que_e": "O jQuery 3.4.1 tem uma falha de XSS (CVE-2020-11022, GHSA-gxr4-xjj5-5px2).",
        "impacto": "Afeta as versões a partir da 1.2 e abaixo da 3.5.0.",
        "como_corrigir": "Atualize o jquery para a 3.5.0.",
        "teste_verificacao": (
            "Depois de atualizar, o site não carrega mais https://loja.exemplo.com.br/js/"
            "jquery-3.4.1.min.js e o console mostra jQuery.fn.jquery igual a 3.5.0."
        ),
        **mudancas,
    }


def motivo_do_descarte(texto: dict[str, str]) -> str:
    mantida, travas_acionadas = conferir_explicacao("jquery", "3.4.1", texto, ENTRADA_DO_JQUERY)
    assert mantida is None
    assert len(travas_acionadas) == 1
    assert travas_acionadas[0].trava == "explicação sem fato novo"
    assert travas_acionadas[0].alvo == "explicação de jquery@3.4.1"
    return travas_acionadas[0].motivo


def test_r21_6_explicacao_que_so_repete_a_entrada_passa() -> None:
    texto = explicacao()

    mantida, travas_acionadas = conferir_explicacao("jquery", "3.4.1", texto, ENTRADA_DO_JQUERY)

    assert mantida == texto
    assert travas_acionadas == []


def test_r21_6_explicacao_sem_fato_nenhum_passa() -> None:
    texto = {"o_que_e": "Biblioteca de JavaScript.", "impacto": "Um atacante pode rodar script."}

    mantida, travas_acionadas = conferir_explicacao("jquery", "3.4.1", texto, ENTRADA_DO_JQUERY)

    assert mantida == texto
    assert travas_acionadas == []


@pytest.mark.parametrize(
    "citacao",
    [
        "cve-2020-11022 e ghsa-GXR4-xjj5-5px2",
        "a versão 3.5.0.",
        "a versão v3.4.1",
        "o arquivo jquery-3.4.1.min.js",
    ],
)
def test_r21_6_mesmo_fato_escrito_de_outro_jeito_passa(citacao: str) -> None:
    mantida, _ = conferir_explicacao(
        "jquery", "3.4.1", explicacao(impacto=f"Veja {citacao}"), ENTRADA_DO_JQUERY
    )

    assert mantida is not None


def test_r21_6_cve_inventado_descarta_a_explicacao() -> None:
    texto = explicacao(impacto="Igual ao CVE-2019-11358, permite XSS.")

    assert motivo_do_descarte(texto) == (
        "explicação descartada: cita o que não estava na entrada: `CVE-2019-11358` (impacto)"
    )


def test_r21_6_ghsa_inventado_descarta() -> None:
    texto = explicacao(o_que_e="Falha descrita no GHSA-6c3j-c64m-qhgq.")

    assert "`GHSA-6c3j-c64m-qhgq` (o_que_e)" in motivo_do_descarte(texto)


def test_r21_6_versao_alvo_inventada_descarta() -> None:
    texto = explicacao(como_corrigir="Atualize o jquery para a 3.7.1.")

    assert "`3.7.1` (como_corrigir)" in motivo_do_descarte(texto)


@pytest.mark.parametrize("versao", ["3.4", "3.4.10", "3.5.0-rc.1", "13.4.1"])
def test_r21_6_versao_parecida_com_a_da_entrada_nao_vale_por_ela(versao: str) -> None:
    texto = explicacao(como_corrigir=f"Atualize para a {versao} ou mais nova.")

    assert f"`{versao}` (como_corrigir)" in motivo_do_descarte(texto)


@pytest.mark.parametrize("porcentagem", ["95%", "95 %", "0,95%", "6.9%"])
def test_r21_6_porcentagem_inventada_descarta(porcentagem: str) -> None:
    texto = explicacao(impacto=f"A chance de exploração é de {porcentagem}.")

    assert f"`{porcentagem}` (impacto)" in motivo_do_descarte(texto)


@pytest.mark.parametrize("cvss", ["6.9", "6,9"])
def test_r21_6_cvss_ou_nota_escritos_pela_ia_descartam(cvss: str) -> None:
    texto = explicacao(impacto=f"O CVSS é {cvss}, risco médio.")

    assert f"`{cvss}` (impacto)" in motivo_do_descarte(texto)


def test_r21_6_lista_cada_fato_novo_uma_vez_numa_trava_so() -> None:
    texto = explicacao(
        o_que_e="Ligado ao CVE-2019-11358 e ao CVE-2019-11358.",
        impacto="Chance de 40%.",
        como_corrigir="Atualize para a 3.7.1.",
    )

    mantida, travas_acionadas = conferir_explicacao("jquery", "3.4.1", texto, ENTRADA_DO_JQUERY)

    assert mantida is None
    assert travas_acionadas == [
        TravaAcionada(
            "explicação sem fato novo",
            "explicação de jquery@3.4.1",
            "explicação descartada: cita o que não estava na entrada: "
            "`CVE-2019-11358` (o_que_e), `40%` (impacto), `3.7.1` (como_corrigir)",
        )
    ]
