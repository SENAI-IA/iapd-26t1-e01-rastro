import io
from email.message import Message
from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError
from urllib.request import Request

import pytest

from rastro.fontes import requisicao_http
from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.requisicao_http import (
    TEMPO_LIMITE_EM_SEGUNDOS,
    baixar_json,
    ler_resposta,
    motivo_do_erro_http,
)

ENDERECO = "https://fonte.exemplo.com/avisos"


class UrlopenFalso:
    def __init__(self, corpo: bytes = b"[]", erro: Exception | None = None) -> None:
        self.corpo = corpo
        self.erro = erro
        self.tempos_limite: list[float] = []

    def __call__(self, requisicao: Request, timeout: float) -> io.BytesIO:
        self.tempos_limite.append(timeout)
        if self.erro is not None:
            raise self.erro
        return io.BytesIO(self.corpo)


def baixar_com(monkeypatch: pytest.MonkeyPatch, urlopen_falso: UrlopenFalso) -> object:
    monkeypatch.setattr(requisicao_http, "urlopen", urlopen_falso)
    return baixar_json(Request(ENDERECO), "Fonte")


def motivo_ao_baixar(monkeypatch: pytest.MonkeyPatch, erro: Exception) -> str:
    with pytest.raises(ConsultaNaoRealizada) as consulta:
        baixar_com(monkeypatch, UrlopenFalso(erro=erro))
    return consulta.value.motivo


def erro_http(codigo: int) -> HTTPError:
    return HTTPError(ENDERECO, codigo, "erro", Message(), None)


def test_r04_1_baixa_e_le_o_json_com_tempo_limite(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(corpo=b'{"nome": "jquery"}')

    assert baixar_com(monkeypatch, urlopen_falso) == {"nome": "jquery"}
    assert urlopen_falso.tempos_limite == [TEMPO_LIMITE_EM_SEGUNDOS]


def test_r04_3_limite_de_consultas_vira_motivo(monkeypatch: pytest.MonkeyPatch) -> None:
    motivo = motivo_ao_baixar(monkeypatch, erro_http(429))

    assert motivo == "limite de consultas do Fonte atingido (HTTP 429)"


def test_r04_3_erro_do_servidor_vira_motivo(monkeypatch: pytest.MonkeyPatch) -> None:
    assert motivo_ao_baixar(monkeypatch, erro_http(503)) == ("erro no servidor do Fonte (HTTP 503)")


def test_r04_3_resposta_que_nao_e_json_vira_motivo(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ConsultaNaoRealizada, match="resposta do Fonte não é JSON"):
        baixar_com(monkeypatch, UrlopenFalso(corpo=b"<html>"))


def test_r04_3_sem_rede_vira_motivo_sem_resposta(monkeypatch: pytest.MonkeyPatch) -> None:
    motivo = motivo_ao_baixar(monkeypatch, URLError("nome não resolvido"))

    assert motivo == "sem resposta do Fonte: nome não resolvido"


def test_r04_3_tempo_esgotado_vira_motivo(monkeypatch: pytest.MonkeyPatch) -> None:
    assert motivo_ao_baixar(monkeypatch, TimeoutError()) == "sem resposta do Fonte: tempo esgotado"


def test_r04_3_conexao_interrompida_vira_motivo(monkeypatch: pytest.MonkeyPatch) -> None:
    motivo = motivo_ao_baixar(monkeypatch, RemoteDisconnected("fechou"))

    assert motivo == "conexão com o Fonte interrompida: fechou"


def test_r04_3_codigos_de_limite_podem_ser_trocados() -> None:
    motivo = motivo_do_erro_http("Fonte", 403, codigos_de_limite=(429,))

    assert motivo == "o Fonte recusou a consulta (HTTP 403)"


def test_r04_3_recusa_usa_o_motivo_informado() -> None:
    motivo = motivo_do_erro_http("Fonte", 404, motivo_da_recusa="pacote não encontrado")

    assert motivo == "pacote não encontrado (HTTP 404)"


def test_r04_1_ler_resposta_devolve_o_que_a_leitura_devolve() -> None:
    def leitura_que_funciona() -> list[int]:
        return [1, 2]

    assert ler_resposta(leitura_que_funciona, "Fonte") == [1, 2]


def test_r04_3_resposta_fora_do_formato_vira_motivo() -> None:
    def leitura_que_falha() -> int:
        resposta: dict[str, int] = {}
        return resposta["campo_que_falta"]

    with pytest.raises(ConsultaNaoRealizada, match="resposta inesperada do Fonte"):
        ler_resposta(leitura_que_falha, "Fonte")
