import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request

from rastro.fontes.filtro_do_pacote_npm import pacote_e_o_npm_procurado
from rastro.fontes.modelos import Aviso, marcar_origem
from rastro.fontes.requisicao_http import baixar_json, ler_resposta

NOME_DA_FONTE = "GitHub Advisory"
ENDERECO_DA_API = "https://api.github.com/advisories"
AVISOS_POR_PAGINA = 100
VERSOES_DO_CVSS_NA_ORDEM = ("cvss_v3", "cvss_v4")


class GitHubAdvisory:
    def __init__(self) -> None:
        self.token = os.environ.get("GITHUB_TOKEN") or None

    def consultar(self, pacote: str, versao: str) -> list[Aviso]:
        resposta = self.baixar_avisos(pacote, versao)

        def converter_os_avisos() -> list[Aviso]:
            return converter_resposta(resposta, pacote)

        return ler_resposta(converter_os_avisos, NOME_DA_FONTE)

    def baixar_avisos(self, pacote: str, versao: str) -> Any:
        return baixar_json(montar_requisicao(pacote, versao, self.token), NOME_DA_FONTE)


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


def converter_resposta(avisos_da_fonte: Any, pacote: str) -> list[Aviso]:
    if not isinstance(avisos_da_fonte, list):
        raise TypeError("a resposta não é uma lista de avisos")
    avisos = []
    for aviso_da_fonte in avisos_da_fonte:
        avisos.extend(avisos_do_pacote(aviso_da_fonte, pacote))
    return avisos


def avisos_do_pacote(aviso_da_fonte: Any, pacote: str) -> list[Aviso]:
    if aviso_retirado(aviso_da_fonte):
        return []
    avisos = []
    for faixa in faixas_do_pacote(aviso_da_fonte, pacote):
        avisos.append(converter_aviso(aviso_da_fonte, faixa))
    return avisos


def aviso_retirado(aviso_da_fonte: Any) -> bool:
    return aviso_da_fonte.get("withdrawn_at") is not None


def faixas_do_pacote(aviso_da_fonte: Any, pacote: str) -> list[Any]:
    faixas = []
    for vulnerabilidade in aviso_da_fonte.get("vulnerabilities") or []:
        if pacote_e_o_npm_procurado(vulnerabilidade["package"], pacote):
            faixas.append(vulnerabilidade)
    return faixas


def converter_aviso(aviso_da_fonte: Any, faixa: Any) -> Aviso:
    ghsa = aviso_da_fonte["ghsa_id"]
    aviso = Aviso(
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
    return marcar_origem(aviso, NOME_DA_FONTE)


def ler_apelidos(aviso_da_fonte: Any, ghsa: str) -> list[str]:
    apelidos = []
    for identificador in aviso_da_fonte.get("identifiers") or []:
        if identificador["value"] != ghsa:
            apelidos.append(identificador["value"])
    return apelidos


def ler_cvss(aviso_da_fonte: Any) -> float | None:
    severidades = aviso_da_fonte.get("cvss_severities")
    if not severidades:
        return None
    for versao_do_cvss in VERSOES_DO_CVSS_NA_ORDEM:
        cvss = severidades.get(versao_do_cvss)
        if cvss and cvss.get("vector_string"):
            return float(cvss["score"])
    return None


def ler_percentil_epss(aviso_da_fonte: Any) -> float | None:
    epss = aviso_da_fonte.get("epss")
    if epss is None or epss.get("percentile") is None:
        return None
    return float(epss["percentile"])
