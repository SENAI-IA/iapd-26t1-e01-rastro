import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rastro.fontes.conector import Aviso, ConsultaNaoRealizada

NOME_DA_FONTE = "GitHub Advisory"
ENDERECO_DA_API = "https://api.github.com/advisories"
TEMPO_LIMITE_EM_SEGUNDOS = 15
AVISOS_POR_PAGINA = 100


class GitHubAdvisory:
    def __init__(self) -> None:
        self.token = os.environ.get("GITHUB_TOKEN") or None

    def consultar(self, pacote: str, versao: str) -> list[Aviso]:
        resposta = self.baixar_avisos(pacote, versao)
        try:
            return converter_resposta(resposta, pacote)
        except (KeyError, TypeError, ValueError, AttributeError) as erro:
            raise ConsultaNaoRealizada(f"resposta inesperada do {NOME_DA_FONTE}") from erro

    def baixar_avisos(self, pacote: str, versao: str) -> Any:
        requisicao = montar_requisicao(pacote, versao, self.token)
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


def montar_requisicao(pacote: str, versao: str, token: str | None) -> Request:
    parametros = {
        "ecosystem": "npm",
        "affects": f"{pacote}@{versao}",
        "per_page": str(AVISOS_POR_PAGINA),
    }
    endereco = f"{ENDERECO_DA_API}?{urlencode(parametros, safe='@/')}"
    cabecalhos = {"Accept": "application/vnd.github+json"}
    if token is not None:
        cabecalhos["Authorization"] = f"Bearer {token}"
    return Request(endereco, headers=cabecalhos)


def motivo_do_erro_http(codigo: int) -> str:
    if codigo in (403, 429):
        return f"limite de consultas do {NOME_DA_FONTE} atingido (HTTP {codigo})"
    if codigo >= 500:
        return f"erro no servidor do {NOME_DA_FONTE} (HTTP {codigo})"
    return f"o {NOME_DA_FONTE} recusou a consulta (HTTP {codigo})"


def converter_resposta(avisos_da_fonte: Any, pacote: str) -> list[Aviso]:
    if not isinstance(avisos_da_fonte, list):
        raise TypeError("a resposta não é uma lista de avisos")
    avisos = []
    for aviso_da_fonte in avisos_da_fonte:
        if aviso_retirado(aviso_da_fonte):
            continue
        for faixa in faixas_do_pacote(aviso_da_fonte, pacote):
            avisos.append(converter_aviso(aviso_da_fonte, faixa))
    return avisos


def aviso_retirado(aviso_da_fonte: Any) -> bool:
    return aviso_da_fonte.get("withdrawn_at") is not None


def faixas_do_pacote(aviso_da_fonte: Any, pacote: str) -> list[Any]:
    faixas = []
    for vulnerabilidade in aviso_da_fonte.get("vulnerabilities") or []:
        if vulnerabilidade_do_pacote_npm(vulnerabilidade, pacote):
            faixas.append(vulnerabilidade)
    return faixas


def vulnerabilidade_do_pacote_npm(vulnerabilidade: Any, pacote: str) -> bool:
    pacote_da_fonte = vulnerabilidade["package"]
    return bool(pacote_da_fonte["ecosystem"] == "npm" and pacote_da_fonte["name"] == pacote)


def converter_aviso(aviso_da_fonte: Any, faixa: Any) -> Aviso:
    ghsa = aviso_da_fonte["ghsa_id"]
    return Aviso(
        fontes=[NOME_DA_FONTE],
        apelidos=ler_apelidos(aviso_da_fonte, ghsa),
        ghsa=ghsa,
        cve=aviso_da_fonte.get("cve_id"),
        resumo=aviso_da_fonte["summary"],
        cvss=ler_cvss(aviso_da_fonte),
        percentil_epss=ler_percentil_epss(aviso_da_fonte),
        versoes_afetadas=faixa["vulnerable_version_range"],
        versao_corrigida=faixa.get("first_patched_version"),
        link=aviso_da_fonte["html_url"],
    )


def ler_apelidos(aviso_da_fonte: Any, ghsa: str) -> list[str]:
    apelidos = []
    for identificador in aviso_da_fonte.get("identifiers") or []:
        if identificador["value"] != ghsa:
            apelidos.append(identificador["value"])
    return apelidos


def ler_cvss(aviso_da_fonte: Any) -> float | None:
    severidades = aviso_da_fonte.get("cvss_severities") or {}
    for versao_do_cvss in ("cvss_v3", "cvss_v4"):
        cvss = severidades.get(versao_do_cvss) or {}
        if cvss.get("vector_string"):
            return float(cvss["score"])
    return None


def ler_percentil_epss(aviso_da_fonte: Any) -> float | None:
    epss = aviso_da_fonte.get("epss")
    if epss is None or epss.get("percentile") is None:
        return None
    return float(epss["percentile"])
