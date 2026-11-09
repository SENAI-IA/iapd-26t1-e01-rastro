import json

import pytest

from rastro.travas.formato import BibliotecaSugerida, conferir_formato

TRECHO_DO_ANGULAR = "let i=e?[`ng-version`,`22.2.2`]:uI(n.selectors[0])"


def resposta(*bibliotecas: dict[str, object]) -> str:
    return json.dumps({"bibliotecas": list(bibliotecas)})


def angular(**mudancas: object) -> dict[str, object]:
    return {"pacote": "@angular/core", "versao": "22.2.2", "trecho": TRECHO_DO_ANGULAR, **mudancas}


def motivo_do_descarte(texto: str) -> str:
    bibliotecas, travas_acionadas = conferir_formato(texto)
    assert bibliotecas == []
    assert len(travas_acionadas) == 1
    assert travas_acionadas[0].trava == "formato fechado"
    assert travas_acionadas[0].alvo == "resposta da IA"
    return travas_acionadas[0].motivo


def test_r21_1_resposta_no_formato_vira_bibliotecas_sugeridas() -> None:
    bibliotecas, travas_acionadas = conferir_formato(resposta(angular()))

    assert bibliotecas == [BibliotecaSugerida("@angular/core", "22.2.2", TRECHO_DO_ANGULAR)]
    assert travas_acionadas == []


def test_r21_1_lista_vazia_e_espacos_em_volta_sao_aceitos() -> None:
    bibliotecas, travas_acionadas = conferir_formato('\n  {"bibliotecas": []}\n')

    assert bibliotecas == []
    assert travas_acionadas == []


def test_r21_1_versao_com_pre_lancamento_e_aceita() -> None:
    bibliotecas, _ = conferir_formato(resposta(angular(versao="22.0.0-rc.1")))

    assert bibliotecas[0].versao == "22.0.0-rc.1"


def test_r21_1_campo_a_mais_na_biblioteca_descarta_a_resposta_inteira() -> None:
    texto = resposta(angular(pacote="jquery", versao="3.4.1"), angular(confianca=0.9))

    assert motivo_do_descarte(texto) == "resposta descartada: campo a mais na biblioteca: confianca"


def test_r21_1_campo_a_mais_na_resposta_descarta() -> None:
    texto = json.dumps({"bibliotecas": [angular()], "observacao": "parece Angular"})

    assert "campo a mais na resposta: observacao" in motivo_do_descarte(texto)


def test_r21_1_campo_faltando_descarta() -> None:
    sem_trecho = {"pacote": "@angular/core", "versao": "22.2.2"}

    assert "campo faltando na biblioteca: trecho" in motivo_do_descarte(resposta(sem_trecho))
    assert "campo faltando na resposta: bibliotecas" in motivo_do_descarte("{}")


@pytest.mark.parametrize(
    "texto",
    [
        "Encontrei o Angular: " + resposta(angular()),
        resposta(angular()) + "\nEspero ter ajudado.",
        "```json\n" + resposta(angular()) + "\n```",
        resposta(angular()) + resposta(angular()),
    ],
)
def test_r21_1_texto_fora_do_json_descarta(texto: str) -> None:
    assert motivo_do_descarte(texto) == "resposta descartada: texto fora do JSON"


@pytest.mark.parametrize(
    ("texto", "motivo"),
    [
        ('{"bibliotecas": [', "JSON inválido"),
        ("[]", "texto fora do JSON"),
        ('{"bibliotecas": {}}', "`bibliotecas` não é uma lista"),
        ('{"bibliotecas": ["@angular/core"]}', "esperado um objeto na biblioteca"),
        ('{"bibliotecas": [], "bibliotecas": [1]}', "campo repetido: `bibliotecas`"),
    ],
)
def test_r21_1_estrutura_fora_do_formato_descarta(texto: str, motivo: str) -> None:
    assert motivo in motivo_do_descarte(texto)


@pytest.mark.parametrize(
    ("mudanca", "motivo"),
    [
        ({"versao": 22}, "`versao` não é texto"),
        ({"pacote": "Angular Core"}, "nome de pacote npm inválido: `Angular Core`"),
        ({"pacote": "@angular/"}, "nome de pacote npm inválido"),
        ({"pacote": "a" * 215}, "nome de pacote npm inválido"),
        ({"versao": "v22.2.2"}, "versão fora do formato x.y.z: `v22.2.2`"),
        ({"versao": "22.2"}, "versão fora do formato x.y.z"),
        ({"versao": "^22.2.2"}, "versão fora do formato x.y.z"),
        ({"trecho": "  "}, "trecho vazio em @angular/core@22.2.2"),
    ],
)
def test_r21_1_campo_invalido_derruba_a_resposta_inteira(
    mudanca: dict[str, object], motivo: str
) -> None:
    texto = resposta(angular(pacote="jquery", versao="3.4.1"), angular(**mudanca))

    assert motivo in motivo_do_descarte(texto)
