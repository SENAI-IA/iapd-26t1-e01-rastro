from dataclasses import dataclass
from datetime import timedelta
from typing import Literal

from rastro.har.modelos import Requisicao

Camada = Literal["pagina", "script", "estilo", "dados", "midia"]

PREFIXOS_DE_MIDIA = ("image/", "font/", "video/", "audio/")


@dataclass(frozen=True)
class PassoDaVisita:
    indice_requisicao: int
    url: str
    camada: Camada
    inicio_ms: float
    duracao_ms: float


def montar_visita(requisicoes: list[Requisicao]) -> list[PassoDaVisita]:
    inicios = {r.indice: r.inicio for r in requisicoes if r.inicio is not None}
    if not inicios:
        return []
    primeiro_inicio = min(inicios.values())
    passos = [
        passo_da_requisicao(requisicao, inicios[requisicao.indice] - primeiro_inicio)
        for requisicao in requisicoes
        if requisicao.indice in inicios
    ]
    return sorted(passos, key=lambda passo: (passo.inicio_ms, passo.indice_requisicao))


def passo_da_requisicao(requisicao: Requisicao, desde_o_inicio: timedelta) -> PassoDaVisita:
    return PassoDaVisita(
        indice_requisicao=requisicao.indice,
        url=requisicao.url,
        camada=camada_do_tipo(requisicao.tipo_conteudo),
        inicio_ms=round(desde_o_inicio.total_seconds() * 1000, 1),
        duracao_ms=round(requisicao.duracao_ms or 0.0, 1),
    )


def camada_do_tipo(tipo_conteudo: str | None) -> Camada:
    tipo = tipo_conteudo or ""
    if tipo == "text/html":
        return "pagina"
    if "javascript" in tipo or "ecmascript" in tipo:
        return "script"
    if tipo == "text/css":
        return "estilo"
    if tipo.startswith(PREFIXOS_DE_MIDIA) or "font" in tipo:
        return "midia"
    return "dados"
