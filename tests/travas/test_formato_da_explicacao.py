import json

from rastro.travas.formato_da_explicacao import conferir_formato_da_explicacao
from rastro.travas.modelos import TravaAcionada

ALVO = "explicação de jquery@3.4.1"
EXPLICACAO_VALIDA = {
    "o_que_e": "Falha de XSS.",
    "impacto": "Rodar código no navegador.",
    "como_corrigir": "Atualizar o jquery.",
    "teste_verificacao": "Conferir a versão carregada.",
}


def test_r07_1_explicacao_no_formato_vira_campos_sem_espacos_em_volta() -> None:
    com_espacos = {**EXPLICACAO_VALIDA, "impacto": "  Rodar código no navegador.  "}

    campos, travas_acionadas = conferir_formato_da_explicacao(json.dumps(com_espacos), ALVO)

    assert campos == EXPLICACAO_VALIDA
    assert travas_acionadas == []


def test_r07_1_explicacao_dentro_de_bloco_de_codigo_e_aceita() -> None:
    cercada = "```json\n" + json.dumps(EXPLICACAO_VALIDA) + "\n```"

    campos, _ = conferir_formato_da_explicacao(cercada, ALVO)

    assert campos == EXPLICACAO_VALIDA


def test_r07_3_explicacao_fora_do_formato_e_descartada_com_o_motivo() -> None:
    vazia = json.dumps({**EXPLICACAO_VALIDA, "como_corrigir": " "})

    campos, travas_acionadas = conferir_formato_da_explicacao(vazia, ALVO)

    assert campos is None
    assert travas_acionadas == [
        TravaAcionada(
            "formato fechado",
            ALVO,
            "explicação descartada: campo vazio na explicação: como_corrigir",
        )
    ]
