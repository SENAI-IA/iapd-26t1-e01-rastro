import json
import subprocess
from typing import Any

import pytest

from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores import codex
from rastro.ia.provedores.codex import ProvedorCodex
from tests.dubles import DADOS

EXECUTAVEL = "/home/auditor/.local/bin/codex"
RESPOSTA_GRAVADA = (DADOS / "codex-resposta.jsonl").read_text(encoding="utf-8")
TEXTO_DA_RESPOSTA = '{"o_que_e": "O jQuery 3.4.1 tem uma falha de XSS na função htmlPrefilter."}'
INICIO_DA_RESPOSTA = '{"type":"thread.started","thread_id":"t"}\n{"type":"turn.started"}\n'


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
    monkeypatch.setattr(codex.subprocess, "run", falso)


def mensagem_do_agente(texto: Any) -> str:
    item = {"id": "item_0", "type": "agent_message", "text": texto}
    return json.dumps({"type": "item.completed", "item": item})


def turno_concluido(uso: Any) -> str:
    return json.dumps({"type": "turn.completed", "usage": uso})


def resposta_com(*linhas: str) -> str:
    return INICIO_DA_RESPOSTA + "\n".join(linhas) + "\n"


def test_r14_4_prompt_vai_pela_entrada_padrao_e_nunca_como_argumento(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    ProvedorCodex(EXECUTAVEL).executar("Explique o GHSA-gxr4-xjj5-5px2")

    assert falso.opcoes[0]["input"] == "Explique o GHSA-gxr4-xjj5-5px2"
    assert all("GHSA" not in argumento for argumento in falso.comandos[0])


def test_r14_4_chama_a_cli_so_leitura_sem_gravar_sessao_em_json_com_tempo_limite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert falso.comandos == [
        [
            EXECUTAVEL,
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--disable",
            "shell_tool",
            "--disable",
            "unified_exec",
            "--ephemeral",
            "--json",
            "-",
        ]
    ]
    assert falso.opcoes[0]["capture_output"] is True
    assert falso.opcoes[0]["encoding"] == "utf-8"
    assert falso.opcoes[0]["errors"] == "replace"
    assert falso.opcoes[0]["timeout"] == 120


def test_r14_4_le_o_texto_do_agent_message_e_soma_os_tokens_do_turno(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())

    resposta = ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert resposta == RespostaDoProvedor(TEXTO_DA_RESPOSTA, tokens=12692 + 152)


def test_r14_4_com_mais_de_um_agent_message_vale_o_ultimo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saida = resposta_com(
        mensagem_do_agente("Vou analisar o aviso."),
        mensagem_do_agente(TEXTO_DA_RESPOSTA),
        turno_concluido({"input_tokens": 10, "output_tokens": 5}),
    )
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    resposta = ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert resposta == RespostaDoProvedor(TEXTO_DA_RESPOSTA, tokens=15)


def test_r14_4_linha_que_nao_e_json_e_ignorada(monkeypatch: pytest.MonkeyPatch) -> None:
    saida = resposta_com(
        "aviso solto da CLI",
        "[]",
        mensagem_do_agente(TEXTO_DA_RESPOSTA),
        turno_concluido({"input_tokens": 10, "output_tokens": 5}),
    )
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    resposta = ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert resposta == RespostaDoProvedor(TEXTO_DA_RESPOSTA, tokens=15)


@pytest.mark.parametrize(
    "linhas_do_turno",
    [
        [],
        [turno_concluido(None)],
        [turno_concluido({"input_tokens": 12692})],
        [turno_concluido({"input_tokens": "12692", "output_tokens": 152})],
        [turno_concluido({"input_tokens": True, "output_tokens": 152})],
        [turno_concluido({"input_tokens": -1, "output_tokens": 152})],
    ],
)
def test_r14_4_usage_ausente_ou_incompleto_deixa_tokens_none_sem_estimar(
    monkeypatch: pytest.MonkeyPatch, linhas_do_turno: list[str]
) -> None:
    saida = resposta_com(mensagem_do_agente(TEXTO_DA_RESPOSTA), *linhas_do_turno)
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    resposta = ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert resposta.texto == TEXTO_DA_RESPOSTA
    assert resposta.tokens is None


def test_r14_4_codigo_de_saida_diferente_de_zero_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(saida="", codigo_de_saida=1))

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Codex terminou com código de saída 1"


def test_r14_4_tempo_limite_estourado_vira_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    def estourar_o_tempo(comando: list[str], **opcoes: Any) -> None:
        raise subprocess.TimeoutExpired(comando, opcoes["timeout"])

    trocar_subprocess(monkeypatch, estourar_o_tempo)

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Codex passou do tempo limite de 120 s"


def test_r14_4_cli_que_sumiu_depois_de_localizada_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def cli_ausente(comando: list[str], **_opcoes: Any) -> None:
        raise FileNotFoundError(2, "No such file or directory", comando[0])

    trocar_subprocess(monkeypatch, cli_ausente)

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo.startswith("a CLI do Codex não pôde ser executada")


@pytest.mark.parametrize(
    "saida",
    [
        "",
        "Você não está logado.",
        resposta_com(turno_concluido({"input_tokens": 10, "output_tokens": 0})),
        resposta_com(mensagem_do_agente("")),
        resposta_com(mensagem_do_agente(None)),
        resposta_com(json.dumps({"type": "item.completed", "item": "texto"})),
        resposta_com(
            json.dumps({"type": "item.completed", "item": {"type": "reasoning", "text": "x"}})
        ),
        resposta_com(json.dumps({"type": "error", "message": "stream disconnected"})),
    ],
)
def test_r14_4_resposta_sem_agent_message_vira_falha(
    monkeypatch: pytest.MonkeyPatch, saida: str
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorCodex(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Codex respondeu sem agent_message"


def test_r14_4_cliente_registra_o_nome_e_os_tokens_do_codex(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())
    ia = ClienteDeIA(ProvedorCodex(EXECUTAVEL))

    assert ia.perguntar("explicar_achado", "prompt") == TEXTO_DA_RESPOSTA
    assert ia.chamadas[0].provedor == "codex"
    assert ia.chamadas[0].tokens == 12844
    assert ia.chamadas[0].sucesso is True
