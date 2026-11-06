from dataclasses import dataclass


@dataclass(frozen=True)
class Cookie:
    nome: str
    http_only: bool
    secure: bool
    same_site: str | None


@dataclass(frozen=True)
class Requisicao:
    indice: int
    url: str
    metodo: str
    status: int
    tipo_conteudo: str | None
    cabecalhos_resposta: dict[str, str]
    cookies_resposta: list[Cookie]
    conteudo: str | None
