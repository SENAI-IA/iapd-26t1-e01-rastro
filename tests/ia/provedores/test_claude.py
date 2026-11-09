import json
import subprocess
from typing import Any

import pytest

from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores import claude
from rastro.ia.provedores.claude import ProvedorClaude
from tests.dubles import DADOS

EXECUTAVEL = "/home/auditor/.local/bin/claude"
RESPOSTA_GRAVADA = (DADOS / "claude-resposta.json").read_text(encoding="utf-8")
TEXTO_DA_RESPOSTA = '{"o_que_e": "O jQuery 3.4.1 tem uma falha de XSS na função htmlPrefilter."}'


class SubprocessFalso:
    def __init__(self, saida: str = RESPOSTA_GRAVADA, codigo_de_saida: int = 0) -> None:
        self.saida = saida
        self.codigo_de_saida = codigo_de_saida
        self.comandos: list[list[str]] = []
        self.opcoes: list[dict[str, Any]] = []

    def __call__(self, comando: list[str], **opcoes: Any) -> subprocess.CompletedProcess[str]:
        self.comandos.append(comando)
        self.opcoes.append(opcoes)
        return subprocess.CompletedProcess(comando, self.codigo_de_saida, self.saida, "")


def trocar_subprocess(monkeypatch: pytest.MonkeyPatch, falso: Any) -> None:
    monkeypatch.setattr(claude.subprocess, "run", falso)


def resposta_com(**campos: Any) -> str:
    resposta = json.loads(RESPOSTA_GRAVADA)
    resposta.update(campos)
    return json.dumps(resposta)


def test_r14_4_prompt_vai_pela_entrada_padrao_e_nunca_como_argumento(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    ProvedorClaude(EXECUTAVEL).executar("Explique o GHSA-gxr4-xjj5-5px2")

    assert falso.opcoes[0]["input"] == "Explique o GHSA-gxr4-xjj5-5px2"
    assert all("GHSA" not in argumento for argumento in falso.comandos[0])


def test_r14_4_chama_a_cli_sem_ferramentas_em_json_com_tempo_limite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    ProvedorClaude(EXECUTAVEL).executar("prompt")

    assert falso.comandos == [[EXECUTAVEL, "-p", "--output-format", "json", "--tools", ""]]
    assert falso.opcoes[0]["capture_output"] is True
    assert falso.opcoes[0]["encoding"] == "utf-8"
    assert falso.opcoes[0]["errors"] == "replace"
    assert falso.opcoes[0]["timeout"] == 120


def test_r14_4_le_o_texto_do_result_e_soma_os_tokens_do_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())

    resposta = ProvedorClaude(EXECUTAVEL).executar("prompt")

    assert resposta == RespostaDoProvedor(TEXTO_DA_RESPOSTA, tokens=2 + 15903 + 11873 + 204)


@pytest.mark.parametrize(
    "uso",
    [
        None,
        {"input_tokens": 2, "output_tokens": 204},
        {
            "input_tokens": "2",
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
            "output_tokens": 204,
        },
    ],
)
def test_r14_4_usage_ausente_ou_incompleto_deixa_tokens_none_sem_estimar(
    monkeypatch: pytest.MonkeyPatch, uso: Any
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(resposta_com(usage=uso)))

    resposta = ProvedorClaude(EXECUTAVEL).executar("prompt")

    assert resposta.texto == TEXTO_DA_RESPOSTA
    assert resposta.tokens is None


def test_r14_4_codigo_de_saida_diferente_de_zero_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(saida="", codigo_de_saida=1))

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorClaude(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Claude terminou com código de saída 1"


def test_r14_4_tempo_limite_estourado_vira_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    def estourar_o_tempo(comando: list[str], **opcoes: Any) -> None:
        raise subprocess.TimeoutExpired(comando, opcoes["timeout"])

    trocar_subprocess(monkeypatch, estourar_o_tempo)

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorClaude(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Claude passou do tempo limite de 120 s"


def test_r14_4_cli_que_sumiu_depois_de_localizada_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def cli_ausente(comando: list[str], **_opcoes: Any) -> None:
        raise FileNotFoundError(2, "No such file or directory", comando[0])

    trocar_subprocess(monkeypatch, cli_ausente)

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorClaude(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo.startswith("a CLI do Claude não pôde ser executada")


@pytest.mark.parametrize(
    ("saida", "motivo"),
    [
        (resposta_com(is_error=True), "a CLI do Claude informou erro na resposta (is_error)"),
        (resposta_com(result=""), "a CLI do Claude respondeu sem texto"),
        (resposta_com(result=None), "a CLI do Claude respondeu sem texto"),
        ("Você não está logado.", "a resposta da CLI do Claude não é JSON"),
        ("[]", "a resposta da CLI do Claude não é um objeto JSON"),
    ],
)
def test_r14_4_resposta_com_erro_ou_sem_texto_vira_falha(
    monkeypatch: pytest.MonkeyPatch, saida: str, motivo: str
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorClaude(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == motivo


def test_r14_4_cliente_registra_o_nome_e_os_tokens_do_claude(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())
    ia = ClienteDeIA(ProvedorClaude(EXECUTAVEL))

    assert ia.perguntar("explicar_achado", "prompt") == TEXTO_DA_RESPOSTA
    assert ia.chamadas[0].provedor == "claude"
    assert ia.chamadas[0].tokens == 27982
    assert ia.chamadas[0].sucesso is True
