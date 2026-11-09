import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from rastro.fontes.conector import Aviso, ConsultaNaoRealizada, marcar_origem
from rastro.travas.faixa_de_versao import FaixaSemver, faixas_dos_eventos_semver

NOME_DA_FONTE = "OSV"
ENDERECO_DA_API = "https://api.osv.dev/v1/query"
ENDERECO_DO_AVISO = "https://osv.dev/vulnerability/"
TEMPO_LIMITE_EM_SEGUNDOS = 15
FAIXA_SEM_SEMVER = FaixaSemver("", None)


class Osv:
    def consultar(self, pacote: str, versao: str) -> list[Aviso]:
        resposta = self.baixar_avisos(pacote, versao)
        try:
            return converter_resposta(resposta, pacote)
        except (KeyError, TypeError, ValueError, AttributeError) as erro:
            raise ConsultaNaoRealizada(f"resposta inesperada do {NOME_DA_FONTE}") from erro

    def baixar_avisos(self, pacote: str, versao: str) -> Any:
        requisicao = montar_requisicao(pacote, versao)
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


def montar_requisicao(pacote: str, versao: str) -> Request:
    consulta = {"package": {"name": pacote, "ecosystem": "npm"}, "version": versao}
    return Request(
        ENDERECO_DA_API,
        data=json.dumps(consulta).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


def motivo_do_erro_http(codigo: int) -> str:
    if codigo == 429:
        return f"limite de consultas do {NOME_DA_FONTE} atingido (HTTP {codigo})"
    if codigo >= 500:
        return f"erro no servidor do {NOME_DA_FONTE} (HTTP {codigo})"
    return f"o {NOME_DA_FONTE} recusou a consulta (HTTP {codigo})"


def converter_resposta(resposta: Any, pacote: str) -> list[Aviso]:
    if not isinstance(resposta, dict):
        raise TypeError("a resposta não é um objeto com avisos")
    avisos = []
    for aviso_da_fonte in resposta.get("vulns") or []:
        if aviso_retirado(aviso_da_fonte):
            continue
        for faixa in faixas_do_pacote(aviso_da_fonte, pacote):
            avisos.append(converter_aviso(aviso_da_fonte, faixa))
    return avisos


def aviso_retirado(aviso_da_fonte: Any) -> bool:
    return aviso_da_fonte.get("withdrawn") is not None


def faixas_do_pacote(aviso_da_fonte: Any, pacote: str) -> list[FaixaSemver]:
    faixas = []
    for afetado in aviso_da_fonte.get("affected") or []:
        if pacote_npm(afetado, pacote):
            faixas.extend(faixas_semver(afetado) or [FAIXA_SEM_SEMVER])
    return faixas


def pacote_npm(afetado: Any, pacote: str) -> bool:
    pacote_da_fonte = afetado["package"]
    return bool(pacote_da_fonte["ecosystem"] == "npm" and pacote_da_fonte["name"] == pacote)


def faixas_semver(afetado: Any) -> list[FaixaSemver]:
    faixas = []
    for faixa in afetado.get("ranges") or []:
        if faixa["type"] == "SEMVER":
            faixas.extend(faixas_dos_eventos_semver(faixa["events"]))
    return faixas


def converter_aviso(aviso_da_fonte: Any, faixa: FaixaSemver) -> Aviso:
    identificadores = [aviso_da_fonte["id"], *(aviso_da_fonte.get("aliases") or [])]
    principal = identificador_principal(identificadores)
    aviso = Aviso(
        fontes=[NOME_DA_FONTE],
        apelidos=[identificador for identificador in identificadores if identificador != principal],
        ghsa=principal,
        cve=primeiro_com_prefixo(identificadores, "CVE-"),
        resumo=aviso_da_fonte.get("summary") or aviso_da_fonte["details"],
        cvss=None,
        percentil_epss=None,
        versoes_afetadas=faixa.faixa,
        versao_corrigida=faixa.versao_corrigida,
        link=f"{ENDERECO_DO_AVISO}{aviso_da_fonte['id']}",
    )
    return marcar_origem(aviso, NOME_DA_FONTE)


def identificador_principal(identificadores: list[str]) -> str:
    return primeiro_com_prefixo(identificadores, "GHSA-") or identificadores[0]


def primeiro_com_prefixo(identificadores: list[str], prefixo: str) -> str | None:
    for identificador in identificadores:
        if identificador.startswith(prefixo):
            return identificador
    return None
