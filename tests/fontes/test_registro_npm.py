import io
from email.message import Message
from urllib.error import HTTPError, URLError
from urllib.request import Request

import pytest

from rastro.fontes import registro_npm
from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.registro_npm import RegistroDePacotes, RegistroNpm


class RespostaFalsa(io.BytesIO):
    def __init__(self, status: int) -> None:
        super().__init__(b"{}")
        self.status = status


class UrlopenFalso:
    def __init__(self, status: int = 200, erro: Exception | None = None) -> None:
        self.status = status
        self.erro = erro
        self.requisicoes: list[Request] = []
        self.tempos_limite: list[float] = []

    def __call__(self, requisicao: Request, timeout: float) -> RespostaFalsa:
        self.requisicoes.append(requisicao)
        self.tempos_limite.append(timeout)
        if self.erro is not None:
            raise self.erro
        return RespostaFalsa(self.status)


def erro_http(codigo: int) -> HTTPError:
    return HTTPError(registro_npm.ENDERECO_DO_REGISTRO, codigo, "erro", Message(), None)


def consultar(
    monkeypatch: pytest.MonkeyPatch, urlopen_falso: UrlopenFalso, pacote: str, versao: str
) -> bool:
    monkeypatch.setattr(registro_npm, "urlopen", urlopen_falso)
    return RegistroNpm().existe(pacote, versao)


def test_r21_4_registro_npm_cumpre_a_interface() -> None:
    registro: RegistroDePacotes = RegistroNpm()

    assert callable(registro.existe)


def test_r21_4_http_200_confirma_que_foi_publicado(monkeypatch: pytest.MonkeyPatch) -> None:
    assert consultar(monkeypatch, UrlopenFalso(200), "jquery", "3.4.1")


def test_r21_4_http_404_diz_que_nao_foi_publicado(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(erro=erro_http(404))

    assert not consultar(monkeypatch, urlopen_falso, "jquery", "9.9.9")


def test_r21_4_consulta_o_pacote_e_a_versao_no_registro(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()

    consultar(monkeypatch, urlopen_falso, "jquery", "3.4.1")

    requisicao = urlopen_falso.requisicoes[0]
    assert requisicao.full_url == "https://registry.npmjs.org/jquery/3.4.1"
    assert urlopen_falso.tempos_limite == [15]


def test_r21_4_pacote_com_escopo_usa_a_barra_codificada(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()

    consultar(monkeypatch, urlopen_falso, "@angular/core", "11.0.0")

    assert urlopen_falso.requisicoes[0].full_url == (
        "https://registry.npmjs.org/@angular%2Fcore/11.0.0"
    )


def test_r16_2_so_le_o_registro_do_npm(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()

    consultar(monkeypatch, urlopen_falso, "jquery", "3.4.1")

    requisicao = urlopen_falso.requisicoes[0]
    assert requisicao.host == "registry.npmjs.org"
    assert requisicao.get_method() == "GET"
    assert requisicao.data is None


@pytest.mark.parametrize(
    ("erro", "motivo"),
    [
        (URLError("sem rede"), "sem resposta do registro do npm: sem rede"),
        (TimeoutError(), "sem resposta do registro do npm: tempo esgotado"),
        (erro_http(429), "limite de consultas do registro do npm atingido (HTTP 429)"),
        (erro_http(503), "erro no servidor do registro do npm (HTTP 503)"),
        (erro_http(401), "resposta inesperada do registro do npm (HTTP 401)"),
    ],
)
def test_r21_9_sem_resposta_do_registro_vira_consulta_nao_realizada(
    monkeypatch: pytest.MonkeyPatch, erro: Exception, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar(monkeypatch, UrlopenFalso(erro=erro), "jquery", "3.4.1")

    assert falha.value.motivo == motivo


def test_r21_9_codigo_de_sucesso_diferente_de_200_nao_confirma(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar(monkeypatch, UrlopenFalso(204), "jquery", "3.4.1")

    assert falha.value.motivo == "resposta inesperada do registro do npm (HTTP 204)"
