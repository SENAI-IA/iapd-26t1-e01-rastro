import io
import json
from email.message import Message
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request

import pytest

from rastro.fluxo import consultar_avisos
from rastro.fontes import osv
from rastro.fontes.conector import Aviso, ConectorDeAvisos, ConsultaNaoRealizada
from rastro.fontes.osv import Osv
from rastro.identificacao.modelos import Biblioteca
from rastro.travas.faixa_de_versao import (
    FaixaSemver,
    descartar_fora_da_faixa,
    faixas_dos_eventos_semver,
)

PASTA_DE_DADOS = Path(__file__).resolve().parents[1] / "dados"
AVISO_SEM_TEXTO = (
    b'{"vulns": [{"id": "OSV-sem-texto",'
    b' "affected": [{"package": {"ecosystem": "npm", "name": "jquery"}}]}]}'
)
JQUERY = Biblioteca(
    pacote="jquery",
    versao="3.4.1",
    metodo="assinatura",
    situacao="confirmada",
    conferida_no_npm=None,
    travas_que_falharam=[],
    evidencias=[],
)


class UrlopenFalso:
    def __init__(self, corpo: bytes = b"{}", erro: Exception | None = None) -> None:
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


def consultar(
    monkeypatch: pytest.MonkeyPatch,
    urlopen_falso: UrlopenFalso,
    pacote: str = "jquery",
    versao: str = "3.4.1",
) -> list[Aviso]:
    monkeypatch.setattr(osv, "urlopen", urlopen_falso)
    return Osv().consultar(pacote, versao)


def avisos_de_exemplo(monkeypatch: pytest.MonkeyPatch) -> list[Aviso]:
    urlopen_falso = UrlopenFalso(resposta_gravada("osv-campos-ausentes.json"))
    return consultar(monkeypatch, urlopen_falso, "pacote-exemplo", "1.0.0")


def erro_http(codigo: int) -> HTTPError:
    return HTTPError(osv.ENDERECO_DA_API, codigo, "erro", Message(), None)


def test_r04a_1_consulta_o_osv_por_pacote_npm_e_versao(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()
    conector: ConectorDeAvisos = Osv()
    monkeypatch.setattr(osv, "urlopen", urlopen_falso)

    conector.consultar("@angular/core", "11.0.0")

    requisicao = urlopen_falso.requisicoes[0]
    assert requisicao.full_url == "https://api.osv.dev/v1/query"
    assert urlsplit(requisicao.full_url).netloc == "api.osv.dev"
    assert requisicao.get_method() == "POST"
    assert requisicao.get_header("Content-type") == "application/json"
    assert isinstance(requisicao.data, bytes)
    assert json.loads(requisicao.data) == {
        "package": {"name": "@angular/core", "ecosystem": "npm"},
        "version": "11.0.0",
    }
    assert urlopen_falso.tempos_limite == [15]


def test_r04a_1_converte_a_resposta_gravada_em_aviso_com_apelidos(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("osv-jquery-3.4.1.json"))

    avisos = consultar(monkeypatch, urlopen_falso)

    assert avisos[0] == Aviso(
        fontes=["OSV"],
        apelidos=["BIT-drupal-2020-11022", "CVE-2020-11022"],
        ghsa="GHSA-gxr4-xjj5-5px2",
        cve="CVE-2020-11022",
        resumo="Potential XSS vulnerability in jQuery",
        cvss=None,
        percentil_epss=None,
        versoes_afetadas=">= 1.12.0, < 3.5.0",
        versao_corrigida="3.5.0",
        link="https://osv.dev/vulnerability/GHSA-gxr4-xjj5-5px2",
        origem_dos_campos={
            "cve": "OSV",
            "resumo": "OSV",
            "versoes_afetadas": "OSV",
            "versao_corrigida": "OSV",
            "link": "OSV",
        },
    )


def test_r04a_1_usa_so_as_faixas_semver_do_proprio_pacote_no_npm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("osv-jquery-3.4.1.json"))

    avisos = consultar(monkeypatch, urlopen_falso)

    faixas = [(aviso.ghsa, aviso.versoes_afetadas, aviso.versao_corrigida) for aviso in avisos]
    assert faixas == [
        ("GHSA-gxr4-xjj5-5px2", ">= 1.12.0, < 3.5.0", "3.5.0"),
        ("GHSA-jpcq-cgw6-v4j6", ">= 1.0.3, < 3.5.0", "3.5.0"),
    ]


def test_r04a_1_sem_ghsa_o_id_do_osv_vira_o_identificador_e_details_o_resumo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sem_ghsa = avisos_de_exemplo(monkeypatch)[0]

    assert sem_ghsa.ghsa == "MAL-2099-0001"
    assert sem_ghsa.apelidos == []
    assert sem_ghsa.cve is None
    assert sem_ghsa.resumo.startswith("Aviso sem GHSA")
    assert sem_ghsa.versoes_afetadas == ">= 0"
    assert sem_ghsa.versao_corrigida is None
    assert sem_ghsa.link == "https://osv.dev/vulnerability/MAL-2099-0001"


def test_r04a_1_ghsa_nos_apelidos_vira_o_identificador_e_o_id_do_osv_vira_apelido(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    duas_faixas = avisos_de_exemplo(monkeypatch)[1:3]

    assert [aviso.ghsa for aviso in duas_faixas] == ["GHSA-gggg-hhhh-iiii"] * 2
    assert duas_faixas[0].apelidos == ["OSV-2099-0002", "CVE-2099-0002"]
    assert duas_faixas[0].cve == "CVE-2099-0002"
    assert [(aviso.versoes_afetadas, aviso.versao_corrigida) for aviso in duas_faixas] == [
        ("< 0.9.0", "0.9.0"),
        (">= 1.0.0, <= 1.0.5", None),
    ]


def test_r04a_1_aviso_sem_faixa_semver_sai_com_faixa_vazia_e_a_trava_6_descarta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sem_faixa = avisos_de_exemplo(monkeypatch)[3]

    mantidos, barrados = descartar_fora_da_faixa("pacote-exemplo", "1.0.0", [sem_faixa])

    assert sem_faixa.ghsa == "OSV-2099-0003"
    assert sem_faixa.versoes_afetadas == ""
    assert mantidos == []
    assert barrados[0].alvo == "OSV-2099-0003 em pacote-exemplo@1.0.0"
    assert "não foi possível conferir a faixa" in barrados[0].motivo


def test_r04a_1_descarta_aviso_retirado(monkeypatch: pytest.MonkeyPatch) -> None:
    identificadores = [aviso.ghsa for aviso in avisos_de_exemplo(monkeypatch)]

    assert "OSV-2099-0004" not in identificadores
    assert len(identificadores) == 4


def test_r04a_1_a_trava_6_vale_igual_para_as_faixas_do_osv(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen_falso = UrlopenFalso(resposta_gravada("osv-jquery-3.4.1.json"))
    avisos = consultar(monkeypatch, urlopen_falso)

    mantidos, barrados = descartar_fora_da_faixa("jquery", "3.4.1", avisos)
    _, fora = descartar_fora_da_faixa("jquery", "3.5.0", avisos)

    assert mantidos == avisos
    assert barrados == []
    assert len(fora) == 2


def test_r04a_1_sem_avisos_devolve_lista_vazia(monkeypatch: pytest.MonkeyPatch) -> None:
    assert consultar(monkeypatch, UrlopenFalso(b"{}")) == []


@pytest.mark.parametrize(
    ("eventos", "esperado"),
    [
        (
            [{"introduced": "1.2.0"}, {"fixed": "3.5.0"}],
            [FaixaSemver(">= 1.2.0, < 3.5.0", "3.5.0")],
        ),
        ([{"introduced": "0"}, {"fixed": "3.5.0"}], [FaixaSemver("< 3.5.0", "3.5.0")]),
        (
            [{"introduced": "1.0.0"}, {"last_affected": "1.0.5"}],
            [FaixaSemver(">= 1.0.0, <= 1.0.5", None)],
        ),
        ([{"introduced": "0"}, {"last_affected": "1.0.5"}], [FaixaSemver("<= 1.0.5", None)]),
        ([{"introduced": "2.0.0"}], [FaixaSemver(">= 2.0.0", None)]),
        ([{"introduced": "0"}], [FaixaSemver(">= 0", None)]),
        ([{"fixed": "1.0.0"}], []),
        ([{"introduced": "1.0.0"}, {"limit": "2.0.0"}], [FaixaSemver(">= 1.0.0", None)]),
        (
            [{"introduced": "0"}, {"fixed": "1.0.0"}, {"introduced": "2.0.0"}, {"fixed": "2.1.0"}],
            [FaixaSemver("< 1.0.0", "1.0.0"), FaixaSemver(">= 2.0.0, < 2.1.0", "2.1.0")],
        ),
    ],
)
def test_r04a_1_le_os_eventos_semver_como_faixa_de_versao(
    eventos: list[dict[str, str]], esperado: list[FaixaSemver]
) -> None:
    assert faixas_dos_eventos_semver(eventos) == esperado


@pytest.mark.parametrize(
    ("erro", "motivo"),
    [
        (URLError("sem rede"), "sem resposta do OSV: sem rede"),
        (TimeoutError(), "sem resposta do OSV: tempo esgotado"),
        (erro_http(429), "limite de consultas do OSV atingido (HTTP 429)"),
        (erro_http(503), "erro no servidor do OSV (HTTP 503)"),
        (erro_http(400), "o OSV recusou a consulta (HTTP 400)"),
    ],
)
def test_r04a_6_falha_do_osv_vira_nao_consultada_com_o_motivo(
    monkeypatch: pytest.MonkeyPatch, erro: Exception, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar(monkeypatch, UrlopenFalso(erro=erro))

    assert falha.value.motivo == motivo


@pytest.mark.parametrize(
    ("corpo", "motivo"),
    [
        (b"<html>fora do ar</html>", "resposta do OSV não é JSON"),
        (b"[]", "resposta inesperada do OSV"),
        (AVISO_SEM_TEXTO, "resposta inesperada do OSV"),
    ],
)
def test_r04a_6_resposta_ilegivel_do_osv_vira_nao_consultada(
    monkeypatch: pytest.MonkeyPatch, corpo: bytes, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar(monkeypatch, UrlopenFalso(corpo))

    assert falha.value.motivo == motivo


def test_r04a_6_falha_do_osv_nao_para_a_consulta_das_bibliotecas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(osv, "urlopen", UrlopenFalso(erro=URLError("sem rede")))

    consultados = consultar_avisos([JQUERY], Osv())

    assert consultados.avisos == []
    assert consultados.nao_consultadas == {"jquery@3.4.1": "sem resposta do OSV: sem rede"}
