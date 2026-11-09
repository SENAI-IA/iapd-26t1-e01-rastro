import json
import os
from dataclasses import dataclass, replace
from http.client import HTTPException
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rastro.fontes.conector import Aviso, ConsultaNaoRealizada

NOME_DA_FONTE = "NVD"
ENDERECO_DA_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
TEMPO_LIMITE_EM_SEGUNDOS = 15
METRICAS_NA_ORDEM = ("cvssMetricV31", "cvssMetricV30", "cvssMetricV40")


class BuscaDeCvss(Protocol):
    def buscar_cvss(self, cve: str) -> float | None: ...


@dataclass(frozen=True)
class CvssCompletado:
    avisos: list[Aviso]
    nao_responderam: dict[str, str]


class Nvd:
    def __init__(self) -> None:
        self.chave = os.environ.get("NVD_API_KEY") or None

    def buscar_cvss(self, cve: str) -> float | None:
        resposta = self.baixar_cve(cve)
        try:
            return ler_cvss(resposta)
        except (KeyError, TypeError, ValueError, AttributeError) as erro:
            raise ConsultaNaoRealizada(f"resposta inesperada do {NOME_DA_FONTE}") from erro

    def baixar_cve(self, cve: str) -> Any:
        requisicao = montar_requisicao(cve, self.chave)
        try:
            with urlopen(requisicao, timeout=TEMPO_LIMITE_EM_SEGUNDOS) as resposta:
                return json.loads(resposta.read().decode("utf-8"))
        except HTTPError as erro:
            raise ConsultaNaoRealizada(motivo_do_erro_http(erro.code)) from erro
        except URLError as erro:
            raise ConsultaNaoRealizada(f"sem resposta do {NOME_DA_FONTE}: {erro.reason}") from erro
        except TimeoutError as erro:
            raise ConsultaNaoRealizada(f"sem resposta do {NOME_DA_FONTE}: tempo esgotado") from erro
        except (UnicodeDecodeError, json.JSONDecodeError) as erro:
            raise ConsultaNaoRealizada(f"resposta do {NOME_DA_FONTE} não é JSON") from erro
        except (HTTPException, OSError) as erro:
            raise ConsultaNaoRealizada(motivo_de_conexao_interrompida(erro)) from erro


def montar_requisicao(cve: str, chave: str | None) -> Request:
    endereco = f"{ENDERECO_DA_API}?{urlencode({'cveId': cve})}"
    cabecalhos = {"Accept": "application/json"}
    if chave is not None:
        cabecalhos["apiKey"] = chave
    return Request(endereco, headers=cabecalhos)


def motivo_de_conexao_interrompida(erro: Exception) -> str:
    return f"conexão com o {NOME_DA_FONTE} interrompida: {erro}"


def motivo_do_erro_http(codigo: int) -> str:
    if codigo in (403, 429):
        return f"limite de consultas do {NOME_DA_FONTE} atingido (HTTP {codigo})"
    if codigo >= 500:
        return f"erro no servidor do {NOME_DA_FONTE} (HTTP {codigo})"
    return f"o {NOME_DA_FONTE} recusou a consulta (HTTP {codigo})"


def ler_cvss(resposta: Any) -> float | None:
    vulnerabilidades = resposta["vulnerabilities"]
    if not vulnerabilidades:
        return None
    metricas = vulnerabilidades[0]["cve"].get("metrics") or {}
    for versao_do_cvss in METRICAS_NA_ORDEM:
        medicoes = metricas.get(versao_do_cvss) or []
        if medicoes:
            return float(medicao_principal(medicoes)["cvssData"]["baseScore"])
    return None


def medicao_principal(medicoes: list[Any]) -> Any:
    for medicao in medicoes:
        if medicao.get("type") == "Primary":
            return medicao
    return medicoes[0]


def completar_cvss(avisos: list[Aviso], nvd: BuscaDeCvss) -> CvssCompletado:
    cvss_por_cve: dict[str, float | None] = {}
    nao_responderam: dict[str, str] = {}
    for cve in cves_sem_cvss(avisos):
        try:
            cvss_por_cve[cve] = nvd.buscar_cvss(cve)
        except ConsultaNaoRealizada as erro:
            nao_responderam[cve] = erro.motivo
    completados = [aplicar_cvss(aviso, cvss_por_cve) for aviso in avisos]
    return CvssCompletado(completados, nao_responderam)


def cves_sem_cvss(avisos: list[Aviso]) -> list[str]:
    cves = [aviso.cve for aviso in avisos if aviso.cve is not None and aviso.cvss is None]
    return list(dict.fromkeys(cves))


def aplicar_cvss(aviso: Aviso, cvss_por_cve: dict[str, float | None]) -> Aviso:
    if aviso.cve is None or aviso.cvss is not None:
        return aviso
    cvss = cvss_por_cve.get(aviso.cve)
    if cvss is None:
        return aviso
    return replace(
        aviso,
        cvss=cvss,
        fontes=[*aviso.fontes, NOME_DA_FONTE],
        origem_dos_campos={**aviso.origem_dos_campos, "cvss": NOME_DA_FONTE},
    )
