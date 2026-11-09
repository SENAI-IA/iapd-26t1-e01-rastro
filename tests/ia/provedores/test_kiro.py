import subprocess
from typing import Any

import pytest

from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores import kiro
from rastro.ia.provedores.kiro import ProvedorKiro
from tests.dubles import DADOS

EXECUTAVEL = "/home/auditor/.local/bin/kiro-cli"
RESPOSTA_GRAVADA = (DADOS / "kiro-resposta.txt").read_text(encoding="utf-8")


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
    monkeypatch.setattr(kiro.subprocess, "run", falso)


def test_r14_4_prompt_vai_pela_entrada_padrao_e_nunca_como_argumento(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    ProvedorKiro(EXECUTAVEL).executar("Explique o GHSA-gxr4-xjj5-5px2")

    assert falso.opcoes[0]["input"] == "Explique o GHSA-gxr4-xjj5-5px2"
    assert all("GHSA" not in argumento for argumento in falso.comandos[0])


def test_r14_4_chama_a_cli_sem_interacao_sem_ferramentas_com_tempo_limite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert falso.comandos == [[EXECUTAVEL, "chat", "--no-interactive", "--trust-tools="]]
    assert falso.opcoes[0]["capture_output"] is True
    assert falso.opcoes[0]["encoding"] == "utf-8"
    assert falso.opcoes[0]["errors"] == "replace"
    assert falso.opcoes[0]["timeout"] == 120


def test_r14_4_le_a_saida_inteira_como_texto_e_deixa_tokens_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())

    resposta = ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert resposta == RespostaDoProvedor(RESPOSTA_GRAVADA.strip(), tokens=None)
    assert resposta.texto.startswith('```json\n{"o_que_e": "A GHSA-gxr4-xjj5-5px2')
    assert "manipulação do DOM" in resposta.texto


def test_r14_4_espacos_e_quebras_em_volta_da_resposta_saem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso('\n  {"o_que_e": "XSS"}\n\n'))

    resposta = ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert resposta.texto == '{"o_que_e": "XSS"}'


@pytest.mark.parametrize("saida", ["", "\n", "   \n\t\n"])
def test_r14_4_saida_vazia_vira_falha(monkeypatch: pytest.MonkeyPatch, saida: str) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Kiro respondeu sem texto"


def test_r14_4_codigo_de_saida_diferente_de_zero_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso(saida="Você não está logado.", codigo_de_saida=1)
    trocar_subprocess(monkeypatch, falso)

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Kiro terminou com código de saída 1"


def test_r14_4_tempo_limite_estourado_vira_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    def estourar_o_tempo(comando: list[str], **opcoes: Any) -> None:
        raise subprocess.TimeoutExpired(comando, opcoes["timeout"])

    trocar_subprocess(monkeypatch, estourar_o_tempo)

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Kiro passou do tempo limite de 120 s"


def test_r14_4_cli_que_sumiu_depois_de_localizada_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def cli_ausente(comando: list[str], **_opcoes: Any) -> None:
        raise FileNotFoundError(2, "No such file or directory", comando[0])

    trocar_subprocess(monkeypatch, cli_ausente)

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo.startswith("a CLI do Kiro não pôde ser executada")


def test_r14_4_cliente_registra_o_nome_do_kiro_e_tokens_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())
    ia = ClienteDeIA(ProvedorKiro(EXECUTAVEL))

    assert ia.perguntar("explicar_achado", "prompt") == RESPOSTA_GRAVADA.strip()
    assert ia.chamadas[0].provedor == "kiro"
    assert ia.chamadas[0].tokens is None
    assert ia.chamadas[0].sucesso is True
