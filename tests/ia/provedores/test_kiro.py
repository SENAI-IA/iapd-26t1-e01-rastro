import json
import subprocess
from typing import Any

import pytest

from rastro.ia.cliente import ClienteDeIA
from rastro.ia.provedor import FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores import execucao_da_cli
from rastro.ia.provedores.kiro import ProvedorKiro
from tests.dubles import DADOS

EXECUTAVEL = "/home/auditor/.local/bin/kiro-cli"
RESPOSTA_GRAVADA = (DADOS / "kiro-resposta.jsonl").read_text(encoding="utf-8")
TEXTO_DA_RESPOSTA = (DADOS / "kiro-resposta.txt").read_text(encoding="utf-8").strip()


def saida_em_eventos(*eventos: dict[str, Any]) -> str:
    return "".join(json.dumps(evento) + "\n" for evento in eventos)


def pedaco(texto: str) -> dict[str, Any]:
    conteudo = {"type": "text", "text": texto}
    return {
        "type": "sessionUpdate",
        "data": {"update": {"sessionUpdate": "agent_message_chunk", "content": conteudo}},
    }


def fim(**dados: Any) -> dict[str, Any]:
    return {"type": "runFinished", "data": dados}


def creditos(*valores: Any, unidade: str = "credit") -> dict[str, Any]:
    medicoes = [{"value": valor, "unit": unidade} for valor in valores]
    return {"type": "metadata", "data": {"meteringUsage": medicoes}}


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
    monkeypatch.setattr(execucao_da_cli.subprocess, "run", falso)


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

    assert falso.comandos == [
        [EXECUTAVEL, "chat", "--no-interactive", "--trust-tools=", "--output-format", "stream-json"]
    ]
    assert falso.opcoes[0]["capture_output"] is True
    assert falso.opcoes[0]["encoding"] == "utf-8"
    assert falso.opcoes[0]["errors"] == "replace"
    assert falso.opcoes[0]["timeout"] == 120


def test_r11_4_le_o_texto_final_e_os_creditos_e_deixa_tokens_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())

    resposta = ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert resposta == RespostaDoProvedor(TEXTO_DA_RESPOSTA, tokens=None, creditos=0.74)
    assert resposta.texto.startswith('```json\n{"o_que_e": "A GHSA-gxr4-xjj5-5px2')
    assert "manipulação do DOM" in resposta.texto


def test_r14_4_espacos_e_quebras_em_volta_da_resposta_saem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saida = saida_em_eventos(fim(status="success", finalText='\n  {"o_que_e": "XSS"}\n\n'))
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    resposta = ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert resposta.texto == '{"o_que_e": "XSS"}'


def test_r14_4_texto_final_cortado_vem_dos_pedacos_da_resposta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cortado = fim(status="success", finalText='{"o_que', finalTextTruncated=True)
    saida = saida_em_eventos(pedaco('{"o_que_e": '), pedaco('"XSS"}'), cortado)
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    resposta = ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert resposta.texto == '{"o_que_e": "XSS"}'


def test_r14_4_linhas_que_nao_sao_json_ficam_de_fora(monkeypatch: pytest.MonkeyPatch) -> None:
    saida = "aviso solto\n[1, 2]\n" + saida_em_eventos(fim(status="success", finalText="ok"))
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    assert ProvedorKiro(EXECUTAVEL).executar("prompt").texto == "ok"


def test_r14_4_status_diferente_de_sucesso_vira_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    saida = saida_em_eventos(fim(status="error", finalText="parcial"))
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    with pytest.raises(FalhaDoProvedor) as falha:
        ProvedorKiro(EXECUTAVEL).executar("prompt")

    assert falha.value.motivo == "a CLI do Kiro terminou com status error"


def test_r11_4_soma_os_creditos_de_todas_as_medicoes(monkeypatch: pytest.MonkeyPatch) -> None:
    saida = saida_em_eventos(creditos(0.5), creditos(0.25), fim(status="success", finalText="ok"))
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    assert ProvedorKiro(EXECUTAVEL).executar("prompt").creditos == 0.75


@pytest.mark.parametrize(
    "medicao",
    [
        creditos(),
        creditos(0.5, unidade="token"),
        creditos("0,5"),
        creditos(True),
        creditos(-1),
    ],
)
def test_r11_2_sem_credito_valido_os_creditos_ficam_none(
    monkeypatch: pytest.MonkeyPatch, medicao: dict[str, Any]
) -> None:
    saida = saida_em_eventos(medicao, fim(status="success", finalText="ok"))
    trocar_subprocess(monkeypatch, SubprocessFalso(saida))

    assert ProvedorKiro(EXECUTAVEL).executar("prompt").creditos is None


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


def test_r14_4_cliente_registra_o_nome_do_kiro_os_creditos_e_tokens_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trocar_subprocess(monkeypatch, SubprocessFalso())
    cliente_de_ia = ClienteDeIA(ProvedorKiro(EXECUTAVEL))

    assert cliente_de_ia.perguntar("explicar_achado", "prompt") == TEXTO_DA_RESPOSTA
    assert cliente_de_ia.chamadas[0].provedor == "kiro"
    assert cliente_de_ia.chamadas[0].tokens is None
    assert cliente_de_ia.chamadas[0].creditos == 0.74
    assert cliente_de_ia.chamadas[0].sucesso is True
