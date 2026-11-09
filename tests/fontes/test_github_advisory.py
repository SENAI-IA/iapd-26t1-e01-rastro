import io
from email.message import Message
from http.client import IncompleteRead, RemoteDisconnected
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request

import pytest

from rastro.fontes import github_advisory
from rastro.fontes.conector import CAMPOS_COM_ORIGEM, Aviso, ConectorDeAvisos, ConsultaNaoRealizada
from rastro.fontes.github_advisory import GitHubAdvisory

PASTA_DE_DADOS = Path(__file__).resolve().parents[1] / "dados"
AVISO_SEM_RESUMO = (
    b'[{"ghsa_id": "GHSA-sem-resumo", "withdrawn_at": null,'
    b' "vulnerabilities": [{"package": {"ecosystem": "npm", "name": "jquery"}}]}]'
)


class UrlopenFalso:
    def __init__(self, corpo: bytes = b"[]", erro: Exception | None = None) -> None:
        self.corpo = corpo
        self.erro = erro
        self.requisicoes: list[Request] = []
        self.tempos_limite: list[float] = []

    def __call__(self, requisicao: Request, timeout: float) -> io.BytesIO:
        self.requisicoes.append(requisicao)
        self.tempos_limite.append(timeout)
        if self.erro is not None:
            raise self.erro
        return io.BytesIO(self.corpo)


def resposta_gravada(nome: str) -> bytes:
    return (PASTA_DE_DADOS / nome).read_bytes()


def trocar_urlopen(monkeypatch: pytest.MonkeyPatch, urlopen_falso: UrlopenFalso) -> None:
    monkeypatch.setattr(github_advisory, "urlopen", urlopen_falso)


def consultar_jquery(
    monkeypatch: pytest.MonkeyPatch, urlopen_falso: UrlopenFalso
) -> list[Aviso]:
    trocar_urlopen(monkeypatch, urlopen_falso)
    return GitHubAdvisory().consultar("jquery", "3.4.1")


def erro_http(codigo: int) -> HTTPError:
    return HTTPError(github_advisory.ENDERECO_DA_API, codigo, "erro", Message(), None)


@pytest.fixture(autouse=True)
def sem_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)


def test_r04_1_consulta_o_ecossistema_npm_por_pacote_e_versao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen_falso = UrlopenFalso()
    trocar_urlopen(monkeypatch, urlopen_falso)

    GitHubAdvisory().consultar("@angular/core", "11.0.0")

    endereco = urlsplit(urlopen_falso.requisicoes[0].full_url)
    assert f"{endereco.scheme}://{endereco.netloc}{endereco.path}" == (
        "https://api.github.com/advisories"
    )
    assert "affects=@angular/core@11.0.0" in endereco.query
    assert parse_qs(endereco.query) == {
        "ecosystem": ["npm"],
        "affects": ["@angular/core@11.0.0"],
        "per_page": ["100"],
    }
    assert urlopen_falso.requisicoes[0].get_header("Accept") == "application/vnd.github+json"
    assert urlopen_falso.tempos_limite == [15]


def test_r04_2_converte_a_resposta_gravada_em_aviso(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("advisory-jquery-3.4.1.json"))

    avisos = consultar_jquery(monkeypatch, urlopen_falso)

    assert avisos[0] == Aviso(
        fontes=["GitHub Advisory"],
        apelidos=["CVE-2020-11022"],
        ghsa="GHSA-gxr4-xjj5-5px2",
        cve="CVE-2020-11022",
        resumo="Potential XSS vulnerability in jQuery",
        cvss=6.9,
        percentil_epss=0.95,
        versoes_afetadas=">= 1.2, < 3.5.0",
        versao_corrigida="3.5.0",
        link="https://github.com/advisories/GHSA-gxr4-xjj5-5px2",
        origem_dos_campos=dict.fromkeys(CAMPOS_COM_ORIGEM, "GitHub Advisory"),
    )


def test_r04_2_usa_so_as_faixas_do_proprio_pacote_no_npm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("advisory-jquery-3.4.1.json"))

    avisos = consultar_jquery(monkeypatch, urlopen_falso)

    faixas = [(aviso.ghsa, aviso.versoes_afetadas, aviso.versao_corrigida) for aviso in avisos]
    assert faixas == [
        ("GHSA-gxr4-xjj5-5px2", ">= 1.2, < 3.5.0", "3.5.0"),
        ("GHSA-jpcq-cgw6-v4j6", ">= 1.0.3, < 3.5.0", "3.5.0"),
        ("GHSA-jpcq-cgw6-v4j6", "< 1.0.3", None),
    ]


def test_r04_2_cvss_com_nota_zero_e_vetor_nulo_conta_como_ausente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("advisory-campos-ausentes.json"))
    trocar_urlopen(monkeypatch, urlopen_falso)

    sem_cvss, so_com_cvss_v4 = GitHubAdvisory().consultar("pacote-exemplo", "1.0.0")

    assert sem_cvss.cvss is None
    assert so_com_cvss_v4.cvss == 8.7


def test_r04_2_sem_a_chave_epss_o_percentil_fica_none(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("advisory-campos-ausentes.json"))
    trocar_urlopen(monkeypatch, urlopen_falso)

    sem_epss, com_epss = GitHubAdvisory().consultar("pacote-exemplo", "1.0.0")

    assert sem_epss.percentil_epss is None
    assert sem_epss.cve is None
    assert sem_epss.apelidos == []
    assert com_epss.percentil_epss == 0.4


def test_r04_2_sem_avisos_devolve_lista_vazia(monkeypatch: pytest.MonkeyPatch) -> None:
    assert consultar_jquery(monkeypatch, UrlopenFalso(b"[]")) == []


@pytest.mark.parametrize(
    ("erro", "motivo"),
    [
        (URLError("sem rede"), "sem resposta do GitHub Advisory: sem rede"),
        (TimeoutError(), "sem resposta do GitHub Advisory: tempo esgotado"),
        (
            RemoteDisconnected("conexão fechada"),
            "conexão com o GitHub Advisory interrompida: conexão fechada",
        ),
        (
            IncompleteRead(b"", 10),
            "conexão com o GitHub Advisory interrompida: "
            "IncompleteRead(0 bytes read, 10 more expected)",
        ),
        (erro_http(403), "limite de consultas do GitHub Advisory atingido (HTTP 403)"),
        (erro_http(429), "limite de consultas do GitHub Advisory atingido (HTTP 429)"),
        (erro_http(502), "erro no servidor do GitHub Advisory (HTTP 502)"),
        (erro_http(422), "o GitHub Advisory recusou a consulta (HTTP 422)"),
    ],
)
def test_r04_3_falha_na_consulta_vira_nao_consultada_com_o_motivo(
    monkeypatch: pytest.MonkeyPatch, erro: Exception, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar_jquery(monkeypatch, UrlopenFalso(erro=erro))

    assert falha.value.motivo == motivo


@pytest.mark.parametrize(
    ("corpo", "motivo"),
    [
        (b"<html>fora do ar</html>", "resposta do GitHub Advisory não é JSON"),
        (b'{"message": "Not Found"}', "resposta inesperada do GitHub Advisory"),
        (AVISO_SEM_RESUMO, "resposta inesperada do GitHub Advisory"),
    ],
)
def test_r04_3_resposta_ilegivel_vira_nao_consultada(
    monkeypatch: pytest.MonkeyPatch, corpo: bytes, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar_jquery(monkeypatch, UrlopenFalso(corpo))

    assert falha.value.motivo == motivo


def test_r04_4_usa_o_token_quando_existe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token-ficticio")
    urlopen_falso = UrlopenFalso()

    consultar_jquery(monkeypatch, urlopen_falso)

    assert urlopen_falso.requisicoes[0].get_header("Authorization") == "Bearer token-ficticio"


@pytest.mark.parametrize("token", [None, ""])
def test_r04_4_sem_token_consulta_sem_autorizacao(
    monkeypatch: pytest.MonkeyPatch, token: str | None
) -> None:
    if token is not None:
        monkeypatch.setenv("GITHUB_TOKEN", token)
    urlopen_falso = UrlopenFalso()

    consultar_jquery(monkeypatch, urlopen_falso)

    assert not urlopen_falso.requisicoes[0].has_header("Authorization")


def test_r04_5_consulta_so_a_api_oficial_do_github(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()
    conector: ConectorDeAvisos = GitHubAdvisory()
    trocar_urlopen(monkeypatch, urlopen_falso)

    conector.consultar("jquery", "3.4.1")

    hosts = [urlsplit(requisicao.full_url).netloc for requisicao in urlopen_falso.requisicoes]
    assert hosts == ["api.github.com"]


def test_r04_6_descarta_aviso_retirado(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("advisory-jquery-3.4.1.json"))

    avisos = consultar_jquery(monkeypatch, urlopen_falso)

    assert "GHSA-xxxx-yyyy-zzzz" not in [aviso.ghsa for aviso in avisos]
