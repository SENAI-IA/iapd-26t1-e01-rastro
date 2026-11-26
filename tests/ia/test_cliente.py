from collections.abc import Iterator

import pytest

from rastro.ia import cliente
from rastro.ia.cliente import ChamadaDaIA, ClienteDeIA
from rastro.ia.provedor import FalhaDoProvedor, RespostaDoProvedor
from tests.dubles import ProvedorFalso


@pytest.fixture
def relogio_de_2_5_segundos(monkeypatch: pytest.MonkeyPatch) -> None:
    instantes: Iterator[float] = iter([100.0, 102.5])
    monkeypatch.setattr(cliente.time, "perf_counter", lambda: next(instantes))


@pytest.mark.usefixtures("relogio_de_2_5_segundos")
def test_r11_1_chamada_com_sucesso_fica_registrada_com_tempo_e_tokens() -> None:
    provedor = ProvedorFalso([RespostaDoProvedor('{"o_que_e": "XSS"}', tokens=12_890)])
    ia = ClienteDeIA(provedor)

    resposta = ia.perguntar("explicar_achado", "Explique o GHSA-gxr4-xjj5-5px2")

    assert resposta == '{"o_que_e": "XSS"}'
    assert provedor.prompts == ["Explique o GHSA-gxr4-xjj5-5px2"]
    assert ia.chamadas == [
        ChamadaDaIA(
            etapa="explicar_achado",
            provedor="falso",
            entrada="Explique o GHSA-gxr4-xjj5-5px2",
            resposta='{"o_que_e": "XSS"}',
            duracao_s=2.5,
            tokens=12_890,
            sucesso=True,
        )
    ]


@pytest.mark.usefixtures("relogio_de_2_5_segundos")
def test_r11_1_falha_do_provedor_fica_registrada_e_devolve_none() -> None:
    provedor = ProvedorFalso([FalhaDoProvedor("código de saída 1")])
    ia = ClienteDeIA(provedor)

    assert ia.perguntar("identificar_bibliotecas", "trechos") is None

    assert ia.chamadas == [
        ChamadaDaIA(
            etapa="identificar_bibliotecas",
            provedor="falso",
            entrada="trechos",
            resposta="código de saída 1",
            duracao_s=2.5,
            tokens=None,
            sucesso=False,
        )
    ]


def test_r11_1_cada_chamada_fica_registrada_na_ordem() -> None:
    provedor = ProvedorFalso(
        [
            RespostaDoProvedor("primeira", tokens=10),
            FalhaDoProvedor("tempo limite estourado"),
            RespostaDoProvedor("terceira", tokens=30),
        ]
    )
    ia = ClienteDeIA(provedor)

    respostas = [ia.perguntar("explicar_achado", f"prompt {n}") for n in range(3)]

    assert respostas == ["primeira", None, "terceira"]
    assert [(c.entrada, c.sucesso, c.tokens) for c in ia.chamadas] == [
        ("prompt 0", True, 10),
        ("prompt 1", False, None),
        ("prompt 2", True, 30),
    ]


def test_r16_3_prompt_sai_sanitizado_e_a_chamada_registra_o_que_foi_enviado() -> None:
    provedor = ProvedorFalso([RespostaDoProvedor("ok", tokens=1)])
    ia = ClienteDeIA(provedor)

    ia.perguntar("identificar_bibliotecas", "trecho de https://loja.exemplo/a.js?sessao=x1")

    enviado = "trecho de https://loja.exemplo/a.js?[removido]"
    assert provedor.prompts == [enviado]
    assert ia.chamadas[0].entrada == enviado


def test_r16_4_resposta_da_ia_fica_registrada_sem_dado_que_parece_segredo() -> None:
    jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.assinatura"
    provedor = ProvedorFalso([RespostaDoProvedor(f"token lido: {jwt}", tokens=1)])
    ia = ClienteDeIA(provedor)

    resposta = ia.perguntar("identificar_bibliotecas", "trecho")

    assert resposta == f"token lido: {jwt}"
    assert ia.chamadas[0].resposta == "token lido: [removido]"


def test_r11_2_provedor_sem_tokens_registra_none_e_nunca_estima() -> None:
    resposta_longa = "texto " * 500
    ia = ClienteDeIA(ProvedorFalso([RespostaDoProvedor(resposta_longa, tokens=None)], "kiro"))

    ia.perguntar("explicar_achado", "prompt")

    assert ia.chamadas[0].tokens is None
    assert ia.chamadas[0].provedor == "kiro"
