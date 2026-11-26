import subprocess
from typing import Any

import pytest

from rastro.ia.provedor import FalhaDoProvedor
from rastro.ia.provedores.execucao_da_cli import TEMPO_LIMITE_EM_SEGUNDOS, executar_cli_da_ia

EXECUTAVEL = "/home/auditor/.local/bin/ia"
PROMPT = "explique o aviso"


class SubprocessFalso:
    def __init__(self, saida: str = "resposta", codigo_de_saida: int = 0) -> None:
        self.saida = saida
        self.codigo_de_saida = codigo_de_saida
        self.comandos: list[list[str]] = []
        self.opcoes: list[dict[str, Any]] = []

    def __call__(self, comando: list[str], **opcoes: Any) -> subprocess.CompletedProcess[str]:
        self.comandos.append(comando)
        self.opcoes.append(opcoes)
        return subprocess.CompletedProcess(comando, self.codigo_de_saida, self.saida, "")


def subprocess_que_falha(erro: Exception) -> Any:
    def executar(comando: list[str], **opcoes: Any) -> subprocess.CompletedProcess[str]:
        raise erro

    return executar


def trocar_subprocess(monkeypatch: pytest.MonkeyPatch, falso: Any) -> None:
    monkeypatch.setattr(subprocess, "run", falso)


def test_r14_4_prompt_vai_pela_entrada_padrao_e_nunca_como_argumento(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    executar_cli_da_ia(EXECUTAVEL, ["--print"], PROMPT, "IA")

    assert falso.comandos == [[EXECUTAVEL, "--print"]]
    assert falso.opcoes[0]["input"] == PROMPT


def test_r14_4_le_a_saida_como_utf8_com_tempo_limite(monkeypatch: pytest.MonkeyPatch) -> None:
    falso = SubprocessFalso()
    trocar_subprocess(monkeypatch, falso)

    executar_cli_da_ia(EXECUTAVEL, [], PROMPT, "IA")

    assert falso.opcoes[0]["encoding"] == "utf-8"
    assert falso.opcoes[0]["timeout"] == TEMPO_LIMITE_EM_SEGUNDOS


def test_r14_4_devolve_a_saida_padrao_da_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(saida="texto da IA"))

    assert executar_cli_da_ia(EXECUTAVEL, [], PROMPT, "IA") == "texto da IA"


def test_r14_4_codigo_de_saida_diferente_de_zero_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso(codigo_de_saida=2))

    with pytest.raises(FalhaDoProvedor, match="a CLI do IA terminou com código de saída 2"):
        executar_cli_da_ia(EXECUTAVEL, [], PROMPT, "IA")


def test_r14_4_tempo_limite_estourado_vira_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    erro = subprocess.TimeoutExpired(EXECUTAVEL, TEMPO_LIMITE_EM_SEGUNDOS)
    trocar_subprocess(monkeypatch, subprocess_que_falha(erro))

    with pytest.raises(FalhaDoProvedor, match="passou do tempo limite"):
        executar_cli_da_ia(EXECUTAVEL, [], PROMPT, "IA")


def test_r14_4_cli_que_nao_pode_ser_executada_vira_falha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, subprocess_que_falha(FileNotFoundError("sumiu")))

    with pytest.raises(FalhaDoProvedor, match="a CLI do IA não pôde ser executada: sumiu"):
        executar_cli_da_ia(EXECUTAVEL, [], PROMPT, "IA")
