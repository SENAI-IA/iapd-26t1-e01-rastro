import json
from typing import Any
from urllib.request import Request

from rastro.fontes.faixas_do_osv import FaixaSemver, faixas_dos_eventos_semver
from rastro.fontes.filtro_do_pacote_npm import pacote_e_o_npm_procurado
from rastro.fontes.modelos import Aviso, marcar_origem
from rastro.fontes.requisicao_http import baixar_json, ler_resposta

NOME_DA_FONTE = "OSV"
ENDERECO_DA_API = "https://api.osv.dev/v1/query"
ENDERECO_DO_AVISO = "https://osv.dev/vulnerability/"
CODIGOS_DE_LIMITE_DO_OSV = (429,)
FAIXA_SEM_SEMVER = FaixaSemver("", None)


class Osv:
    def consultar(self, pacote: str, versao: str) -> list[Aviso]:
        resposta = self.baixar_avisos(pacote, versao)
        return ler_resposta(lambda: converter_resposta(resposta, pacote), NOME_DA_FONTE)

    def baixar_avisos(self, pacote: str, versao: str) -> Any:
        requisicao = montar_requisicao(pacote, versao)
        return baixar_json(requisicao, NOME_DA_FONTE, CODIGOS_DE_LIMITE_DO_OSV)


def montar_requisicao(pacote: str, versao: str) -> Request:
    consulta = {"package": {"name": pacote, "ecosystem": "npm"}, "version": versao}
    return Request(
        ENDERECO_DA_API,
        data=json.dumps(consulta).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )


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
        if pacote_e_o_npm_procurado(afetado["package"], pacote):
            faixas.extend(faixas_semver(afetado) or [FAIXA_SEM_SEMVER])
    return faixas


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
