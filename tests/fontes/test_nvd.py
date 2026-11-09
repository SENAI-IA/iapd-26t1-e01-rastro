import io
from email.message import Message
from http.client import IncompleteRead, RemoteDisconnected
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request

import pytest

from rastro.fontes import nvd
from rastro.fontes.conector import Aviso, ConsultaNaoRealizada
from rastro.fontes.nvd import BuscaDeCvss, Nvd, completar_cvss
from tests.dubles import NvdFalso

PASTA_DE_DADOS = Path(__file__).resolve().parents[1] / "dados"
SEM_RESULTADO = b'{"totalResults": 0, "vulnerabilities": []}'
SEM_METRICAS = b'{"vulnerabilities": [{"cve": {"id": "CVE-2099-0002", "metrics": {}}}]}'
MEDICAO_SEM_DADOS = b'{"vulnerabilities": [{"cve": {"metrics": {"cvssMetricV31": [{}]}}}]}'


class UrlopenFalso:
    def __init__(self, corpo: bytes = SEM_RESULTADO, erro: Exception | None = None) -> None:
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


def buscar(monkeypatch: pytest.MonkeyPatch, urlopen_falso: UrlopenFalso, cve: str) -> float | None:
    monkeypatch.setattr(nvd, "urlopen", urlopen_falso)
    return Nvd().buscar_cvss(cve)


def erro_http(codigo: int) -> HTTPError:
    return HTTPError(nvd.ENDERECO_DA_API, codigo, "erro", Message(), None)


def aviso(ghsa: str, cve: str | None, cvss: float | None, fontes: list[str] | None = None) -> Aviso:
    return Aviso(
        fontes=fontes or ["GitHub Advisory"],
        apelidos=[cve] if cve else [],
        ghsa=ghsa,
        cve=cve,
        resumo="Aviso de exemplo",
        cvss=cvss,
        percentil_epss=None,
        versoes_afetadas="< 3.5.0",
        versao_corrigida="3.5.0",
        link=f"https://github.com/advisories/{ghsa}",
    )


def test_r04a_2_consulta_o_nvd_pelo_cve(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NVD_API_KEY", raising=False)
    urlopen_falso = UrlopenFalso()

    buscar(monkeypatch, urlopen_falso, "CVE-2020-11022")

    requisicao = urlopen_falso.requisicoes[0]
    endereco = urlsplit(requisicao.full_url)
    assert endereco.netloc == "services.nvd.nist.gov"
    assert endereco.path == "/rest/json/cves/2.0"
    assert parse_qs(endereco.query) == {"cveId": ["CVE-2020-11022"]}
    assert requisicao.get_method() == "GET"
    assert requisicao.get_header("Accept") == "application/json"
    assert requisicao.get_header("Apikey") is None
    assert urlopen_falso.tempos_limite == [15]


def test_r04a_7_usa_a_nvd_api_key_quando_existe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NVD_API_KEY", "chave-de-teste")
    urlopen_falso = UrlopenFalso()

    buscar(monkeypatch, urlopen_falso, "CVE-2020-11022")

    assert urlopen_falso.requisicoes[0].get_header("Apikey") == "chave-de-teste"


def test_r04a_7_nvd_api_key_vazia_conta_como_ausente(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NVD_API_KEY", "")
    urlopen_falso = UrlopenFalso()

    buscar(monkeypatch, urlopen_falso, "CVE-2020-11022")

    assert urlopen_falso.requisicoes[0].get_header("Apikey") is None


def test_r04a_2_le_o_cvss_v3_da_analise_do_proprio_nvd(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("nvd-cve-2020-11022.json"))

    assert buscar(monkeypatch, urlopen_falso, "CVE-2020-11022") == 6.1


def test_r04a_2_sem_cvss_v3_usa_o_v4_e_ignora_o_v2(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("nvd-campos-ausentes.json"))

    assert buscar(monkeypatch, urlopen_falso, "CVE-2099-0001") == 9.3


@pytest.mark.parametrize("corpo", [SEM_RESULTADO, SEM_METRICAS])
def test_r04a_2_cve_desconhecido_ou_sem_metricas_fica_sem_cvss(
    monkeypatch: pytest.MonkeyPatch, corpo: bytes
) -> None:
    assert buscar(monkeypatch, UrlopenFalso(corpo), "CVE-2099-0002") is None


def test_r04a_2_aviso_sem_cvss_ganha_o_do_nvd_com_a_fonte_registrada() -> None:
    sem_cvss = aviso("GHSA-gxr4-xjj5-5px2", "CVE-2020-11022", None)

    completado = completar_cvss([sem_cvss], NvdFalso({"CVE-2020-11022": 6.1}))

    assert completado.avisos[0].cvss == 6.1
    assert completado.avisos[0].fontes == ["GitHub Advisory", "NVD"]
    assert completado.nao_responderam == {}


def test_r04a_2_so_consulta_aviso_com_cve_e_sem_cvss() -> None:
    com_cvss = aviso("GHSA-aaaa-aaaa-aaaa", "CVE-2099-0001", 7.5)
    sem_cve = aviso("GHSA-bbbb-bbbb-bbbb", None, None)
    sem_cvss = aviso("GHSA-cccc-cccc-cccc", "CVE-2099-0003", None)
    nvd_falso = NvdFalso({"CVE-2099-0001": 1.0, "CVE-2099-0003": 5.0})

    completado = completar_cvss([com_cvss, sem_cve, sem_cvss], nvd_falso)

    assert nvd_falso.consultados == ["CVE-2099-0003"]
    assert completado.avisos[:2] == [com_cvss, sem_cve]
    assert completado.avisos[2].cvss == 5.0


def test_r04a_2_faz_uma_consulta_por_cve() -> None:
    do_github = aviso("GHSA-gxr4-xjj5-5px2", "CVE-2020-11022", None)
    do_osv = aviso("GHSA-gxr4-xjj5-5px2", "CVE-2020-11022", None, fontes=["OSV"])
    nvd_falso = NvdFalso({"CVE-2020-11022": 6.1})

    completado = completar_cvss([do_github, do_osv, do_github], nvd_falso)

    assert nvd_falso.consultados == ["CVE-2020-11022"]
    assert [completo.cvss for completo in completado.avisos] == [6.1, 6.1, 6.1]
    assert completado.avisos[1].fontes == ["OSV", "NVD"]


def test_r04a_2_sem_cvss_no_nvd_o_aviso_segue_igual() -> None:
    sem_cvss = aviso("GHSA-cccc-cccc-cccc", "CVE-2099-0003", None)

    completado = completar_cvss([sem_cvss], NvdFalso({"CVE-2099-0003": None}))

    assert completado.avisos == [sem_cvss]


def test_r04a_6_falha_do_nvd_mantem_o_aviso_e_registra_o_motivo() -> None:
    sem_cvss = aviso("GHSA-cccc-cccc-cccc", "CVE-2099-0003", None)
    outro = aviso("GHSA-dddd-dddd-dddd", "CVE-2099-0004", None)
    nvd_falso: BuscaDeCvss = NvdFalso(
        {"CVE-2099-0004": 8.1}, falhas={"CVE-2099-0003": "sem resposta do NVD: sem rede"}
    )

    completado = completar_cvss([sem_cvss, sem_cvss, outro], nvd_falso)

    assert completado.avisos[:2] == [sem_cvss, sem_cvss]
    assert completado.avisos[2].cvss == 8.1
    assert completado.nao_responderam == {"CVE-2099-0003": "sem resposta do NVD: sem rede"}


@pytest.mark.parametrize(
    ("erro", "motivo"),
    [
        (URLError("sem rede"), "sem resposta do NVD: sem rede"),
        (TimeoutError(), "sem resposta do NVD: tempo esgotado"),
        (
            RemoteDisconnected("conexão fechada"),
            "conexão com o NVD interrompida: conexão fechada",
        ),
        (
            IncompleteRead(b"", 10),
            "conexão com o NVD interrompida: IncompleteRead(0 bytes read, 10 more expected)",
        ),
        (erro_http(403), "limite de consultas do NVD atingido (HTTP 403)"),
        (erro_http(429), "limite de consultas do NVD atingido (HTTP 429)"),
        (erro_http(503), "erro no servidor do NVD (HTTP 503)"),
        (erro_http(404), "o NVD recusou a consulta (HTTP 404)"),
    ],
)
def test_r04a_6_falha_do_nvd_vira_nao_consultada_com_o_motivo(
    monkeypatch: pytest.MonkeyPatch, erro: Exception, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        buscar(monkeypatch, UrlopenFalso(erro=erro), "CVE-2020-11022")

    assert falha.value.motivo == motivo


@pytest.mark.parametrize(
    ("corpo", "motivo"),
    [
        (b"<html>fora do ar</html>", "resposta do NVD não é JSON"),
        (b"[]", "resposta inesperada do NVD"),
        (MEDICAO_SEM_DADOS, "resposta inesperada do NVD"),
    ],
)
def test_r04a_6_resposta_ilegivel_do_nvd_vira_nao_consultada(
    monkeypatch: pytest.MonkeyPatch, corpo: bytes, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        buscar(monkeypatch, UrlopenFalso(corpo), "CVE-2020-11022")

    assert falha.value.motivo == motivo
