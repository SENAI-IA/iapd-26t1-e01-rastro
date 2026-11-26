import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request

from rastro.fontes.requisicao_http import baixar_json, ler_resposta

NOME_DA_FONTE = "NVD"
ENDERECO_DA_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
METRICAS_NA_ORDEM = ("cvssMetricV31", "cvssMetricV30", "cvssMetricV40")


class Nvd:
    def __init__(self) -> None:
        self.chave = os.environ.get("NVD_API_KEY") or None

    def buscar_cvss(self, cve: str) -> float | None:
        resposta = self.baixar_cve(cve)

        def ler_o_cvss() -> float | None:
            return ler_cvss(resposta)

        return ler_resposta(ler_o_cvss, NOME_DA_FONTE)

    def baixar_cve(self, cve: str) -> Any:
        return baixar_json(montar_requisicao(cve, self.chave), NOME_DA_FONTE)


def montar_requisicao(cve: str, chave: str | None) -> Request:
    endereco = f"{ENDERECO_DA_API}?{urlencode({'cveId': cve})}"
    cabecalhos = {"Accept": "application/json"}
    if chave is not None:
        cabecalhos["apiKey"] = chave
    return Request(endereco, headers=cabecalhos)


def ler_cvss(resposta: Any) -> float | None:
    vulnerabilidades = resposta["vulnerabilities"]
    if not vulnerabilidades:
        return None
    metricas = vulnerabilidades[0]["cve"].get("metrics")
    if not metricas:
        return None
    for versao_do_cvss in METRICAS_NA_ORDEM:
        medicoes = metricas.get(versao_do_cvss)
        if medicoes:
            return float(medicao_principal(medicoes)["cvssData"]["baseScore"])
    return None


def medicao_principal(medicoes: list[Any]) -> Any:
    for medicao in medicoes:
        if medicao.get("type") == "Primary":
            return medicao
    return medicoes[0]
