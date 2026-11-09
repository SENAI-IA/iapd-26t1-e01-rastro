import json

import pytest

from rastro.explicacao.ia import ETAPA, explicar_achados
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.conector import Aviso
from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.identificacao.modelos import Biblioteca, Evidencia, SituacaoDaBiblioteca
from rastro.risco.modelos import Achado
from rastro.risco.nota import calcular_nota
from tests.dubles import DADOS, ProvedorFalso

RESPOSTA_VALIDA = {
    "o_que_e": "O jquery 3.4.1 tem uma falha de XSS (GHSA-gxr4-xjj5-5px2).",
    "impacto": "Um atacante pode rodar código no navegador de quem acessa o site.",
    "como_corrigir": "Atualizar o jquery para a versão 3.5.0.",
    "teste_verificacao": "Abrir o site e conferir que o jquery carregado é o 3.5.0.",
}


def biblioteca(
    pacote: str = "jquery",
    versao: str = "3.4.1",
    situacao: SituacaoDaBiblioteca = "confirmada",
    url: str | None = "https://loja.exemplo.com/js/jquery.min.js?v=3.4.1&token=abc",
) -> Biblioteca:
    evidencias = [] if url is None else [Evidencia(1, url, "/*! jQuery v3.4.1")]
    return Biblioteca(pacote, versao, "assinatura", situacao, True, [], evidencias)


def achado(
    da_biblioteca: Biblioteca,
    ghsa: str = "GHSA-gxr4-xjj5-5px2",
    cvss: float = 6.1,
    resumo: str = "Potential XSS vulnerability in jQuery",
) -> Achado:
    aviso = Aviso(
        fontes=["GitHub Advisory"],
        apelidos=["CVE-2020-11022"],
        ghsa=ghsa,
        cve="CVE-2020-11022",
        resumo=resumo,
        cvss=cvss,
        percentil_epss=0.97,
        versoes_afetadas=">= 1.2, < 3.5.0",
        versao_corrigida="3.5.0",
        link=f"https://github.com/advisories/{ghsa}",
    )
    return Achado(da_biblioteca, aviso, calcular_nota(cvss, 0.97))


def ia_que_responde(*textos: str) -> tuple[ClienteDeIA, ProvedorFalso]:
    provedor = ProvedorFalso([RespostaDoProvedor(texto, tokens=None) for texto in textos])
    return ClienteDeIA(provedor), provedor


def entrada_enviada(prompt: str) -> dict[str, object]:
    bloco = prompt.rsplit("```json\n", 1)[1].split("\n```", 1)[0]
    dados: dict[str, object] = json.loads(bloco)
    return dados


def test_r07_1_resposta_valida_vira_explicacao_marcada_como_ia() -> None:
    ia, _ = ia_que_responde(json.dumps(RESPOSTA_VALIDA, ensure_ascii=False))

    resultado = explicar_achados([achado(biblioteca())], ia)

    assert resultado.explicacoes == {
        "jquery@3.4.1": Explicacao(**RESPOSTA_VALIDA, gerada_por_ia=True)
    }
    assert resultado.travas_acionadas == []


def test_r07_1_aceita_a_resposta_dentro_de_um_bloco_de_codigo() -> None:
    cercada = "```json\n" + json.dumps(RESPOSTA_VALIDA, ensure_ascii=False) + "\n```"
    ia, _ = ia_que_responde(cercada)

    resultado = explicar_achados([achado(biblioteca())], ia)

    assert resultado.explicacoes["jquery@3.4.1"].gerada_por_ia is True


def test_r07_1_pede_uma_explicacao_por_biblioteca_com_achados() -> None:
    jquery = biblioteca()
    lodash = biblioteca("lodash", "4.17.4", url="https://cdn.exemplo.net/lodash.js")
    resposta = json.dumps(RESPOSTA_VALIDA, ensure_ascii=False)
    ia, provedor = ia_que_responde(resposta, resposta)

    achados = [
        achado(jquery),
        achado(lodash, "GHSA-jf85-cpcp-j695"),
        achado(jquery, "GHSA-jpcq-cgw6-v4j6"),
    ]

    resultado = explicar_achados(achados, ia)

    assert list(resultado.explicacoes) == ["jquery@3.4.1", "lodash@4.17.4"]
    assert len(provedor.prompts) == 2
    assert [chamada.etapa for chamada in ia.chamadas] == [ETAPA, ETAPA]


def test_r07_1_biblioteca_a_confirmar_nao_e_explicada() -> None:
    ia, provedor = ia_que_responde()

    resultado = explicar_achados([achado(biblioteca(situacao="a_confirmar"))], ia)

    assert resultado.explicacoes == {}
    assert provedor.prompts == []


def test_r07_1_prompt_pede_so_json_e_proibe_fato_fora_da_entrada() -> None:
    ia, provedor = ia_que_responde(json.dumps(RESPOSTA_VALIDA))

    explicar_achados([achado(biblioteca())], ia)

    prompt = provedor.prompts[0]
    assert "Responda **só** com um objeto JSON" in prompt
    assert "Não afirme nada sobre o site além do que a entrada traz" in prompt
    assert "{{entrada}}" not in prompt


def test_r07_2_envia_so_pacote_versao_avisos_e_url_sem_query_string() -> None:
    ia, provedor = ia_que_responde(json.dumps(RESPOSTA_VALIDA))

    explicar_achados([achado(biblioteca())], ia)

    assert entrada_enviada(provedor.prompts[0]) == {
        "pacote": "jquery",
        "versao": "3.4.1",
        "url_do_script": "https://loja.exemplo.com/js/jquery.min.js",
        "avisos": [
            {
                "ids": ["GHSA-gxr4-xjj5-5px2", "CVE-2020-11022"],
                "resumo": "Potential XSS vulnerability in jQuery",
                "versoes_afetadas": ">= 1.2, < 3.5.0",
                "versao_corrigida": "3.5.0",
            }
        ],
    }


def test_r07_2_biblioteca_sem_evidencia_vai_sem_url() -> None:
    ia, provedor = ia_que_responde(json.dumps(RESPOSTA_VALIDA))

    explicar_achados([achado(biblioteca(url=None))], ia)

    assert entrada_enviada(provedor.prompts[0])["url_do_script"] is None


def test_r07_3_falha_da_ia_usa_o_resumo_do_aviso_sem_explicacao_da_ia() -> None:
    ia = ClienteDeIA(ProvedorFalso([FalhaDoProvedor("tempo limite")]))

    resultado = explicar_achados([achado(biblioteca())], ia)

    explicacao = resultado.explicacoes["jquery@3.4.1"]
    assert explicacao.gerada_por_ia is False
    assert explicacao.o_que_e == "Potential XSS vulnerability in jQuery"
    assert explicacao.impacto == "Potential XSS vulnerability in jQuery"
    assert explicacao.teste_verificacao == ""
    assert resultado.travas_acionadas == []


def test_r07_3_sem_explicacao_usa_o_resumo_do_aviso_de_maior_nota() -> None:
    jquery = biblioteca()
    ia, _ = ia_que_responde("não sei")

    resultado = explicar_achados(
        [
            achado(jquery, "GHSA-gxr4-xjj5-5px2", cvss=4.0, resumo="Menor"),
            achado(jquery, "GHSA-jpcq-cgw6-v4j6", cvss=9.0, resumo="Maior"),
        ],
        ia,
    )

    assert resultado.explicacoes["jquery@3.4.1"].o_que_e == "Maior"


@pytest.mark.parametrize(
    ("resposta", "motivo"),
    [
        ("não sei", "texto fora do JSON"),
        ('Aqui está: {"o_que_e": "x"}', "texto fora do JSON"),
        (json.dumps(RESPOSTA_VALIDA) + " Espero ter ajudado.", "texto fora do JSON"),
        ('{"o_que_e": ', "JSON inválido"),
        (json.dumps({**RESPOSTA_VALIDA, "nota": "8,2"}), "campo a mais na explicação: nota"),
        (
            json.dumps({"o_que_e": "x", "impacto": "y", "como_corrigir": "z"}),
            "campo faltando na explicação: teste_verificacao",
        ),
        (json.dumps({**RESPOSTA_VALIDA, "impacto": 3}), "`impacto` não é texto"),
        (
            json.dumps({**RESPOSTA_VALIDA, "teste_verificacao": "  "}),
            "campo vazio na explicação: teste_verificacao",
        ),
        ('{"o_que_e": "a", "o_que_e": "b"}', "campo repetido: `o_que_e`"),
    ],
)
def test_r07_3_resposta_fora_do_formato_usa_o_resumo_do_aviso(resposta: str, motivo: str) -> None:
    ia, _ = ia_que_responde(resposta)

    resultado = explicar_achados([achado(biblioteca())], ia)

    assert resultado.explicacoes["jquery@3.4.1"].gerada_por_ia is False
    [trava] = resultado.travas_acionadas
    assert trava.trava == "formato fechado"
    assert trava.alvo == "explicação de jquery@3.4.1"
    assert trava.motivo.startswith("explicação descartada: ")
    assert motivo in trava.motivo


def test_r07_3_resposta_real_do_kiro_sem_todos_os_campos_e_descartada() -> None:
    resposta_gravada = (DADOS / "kiro-resposta.txt").read_text(encoding="utf-8")
    ia, _ = ia_que_responde(resposta_gravada)

    resultado = explicar_achados([achado(biblioteca())], ia)

    assert resultado.explicacoes["jquery@3.4.1"].gerada_por_ia is False
    assert "campo faltando na explicação" in resultado.travas_acionadas[0].motivo


def test_r07_3_explicacao_com_fato_novo_usa_o_resumo_do_aviso() -> None:
    inventada = {**RESPOSTA_VALIDA, "impacto": "Explorada em 95% dos casos (CVE-2020-11023)."}
    ia, _ = ia_que_responde(json.dumps(inventada, ensure_ascii=False))

    resultado = explicar_achados([achado(biblioteca())], ia)

    assert resultado.explicacoes["jquery@3.4.1"].gerada_por_ia is False
    [trava] = resultado.travas_acionadas
    assert trava.trava == "explicação sem fato novo"
    assert "`95%` (impacto)" in trava.motivo
    assert "`CVE-2020-11023` (impacto)" in trava.motivo


def test_r07_3_fato_do_exemplo_do_prompt_nao_conta_como_entrada() -> None:
    copiada = {**RESPOSTA_VALIDA, "como_corrigir": "Atualizar para a versão 1.3.0."}
    ia, _ = ia_que_responde(json.dumps(copiada, ensure_ascii=False))

    resultado = explicar_achados([achado(biblioteca())], ia)

    assert resultado.explicacoes["jquery@3.4.1"].gerada_por_ia is False
    assert "`1.3.0` (como_corrigir)" in resultado.travas_acionadas[0].motivo


def test_r14_5_sem_ia_nao_ha_explicacao() -> None:
    resultado = explicar_achados([achado(biblioteca())], None)

    assert resultado.explicacoes == {}
    assert resultado.travas_acionadas == []
