from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from rastro.har.modelos import Requisicao

Camada = Literal["pagina", "script", "estilo", "dados", "midia"]

PREFIXOS_DE_MIDIA = ("image/", "font/", "video/", "audio/")
MILISSEGUNDOS_POR_SEGUNDO = 1000


@dataclass(frozen=True)
class PassoDaVisita:
    indice_requisicao: int
    url: str
    camada: Camada
    inicio_ms: float
    duracao_ms: float


def montar_visita(requisicoes: list[Requisicao]) -> list[PassoDaVisita]:
    inicios = inicio_de_cada_requisicao(requisicoes)
    if not inicios:
        return []
    primeiro_inicio = min(inicios.values())
    passos = []
    for requisicao in requisicoes:
        if requisicao.indice in inicios:
            desde_o_inicio = inicios[requisicao.indice] - primeiro_inicio
            passos.append(passo_da_requisicao(requisicao, desde_o_inicio))
    return sorted(passos, key=ordem_do_passo)


def inicio_de_cada_requisicao(requisicoes: list[Requisicao]) -> dict[int, datetime]:
    inicios = {}
    for requisicao in requisicoes:
        if requisicao.inicio is not None:
            inicios[requisicao.indice] = requisicao.inicio
    return inicios


def ordem_do_passo(passo: PassoDaVisita) -> tuple[float, int]:
    return (passo.inicio_ms, passo.indice_requisicao)


def passo_da_requisicao(requisicao: Requisicao, desde_o_inicio: timedelta) -> PassoDaVisita:
    return PassoDaVisita(
        indice_requisicao=requisicao.indice,
        url=requisicao.url,
        camada=camada_do_tipo(requisicao.tipo_conteudo),
        inicio_ms=round(desde_o_inicio.total_seconds() * MILISSEGUNDOS_POR_SEGUNDO, 1),
        duracao_ms=round(duracao_ou_zero(requisicao.duracao_ms), 1),
    )


def duracao_ou_zero(duracao_ms: float | None) -> float:
    if not duracao_ms:
        return 0.0
    return duracao_ms


def camada_do_tipo(tipo_conteudo: str | None) -> Camada:
    tipo = tipo_conteudo or ""
    if tipo == "text/html":
        return "pagina"
    if tipo_de_script(tipo):
        return "script"
    if tipo == "text/css":
        return "estilo"
    if tipo_de_midia(tipo):
        return "midia"
    return "dados"


def tipo_de_script(tipo: str) -> bool:
    return "javascript" in tipo or "ecmascript" in tipo


def tipo_de_midia(tipo: str) -> bool:
    return tipo.startswith(PREFIXOS_DE_MIDIA) or "font" in tipo
