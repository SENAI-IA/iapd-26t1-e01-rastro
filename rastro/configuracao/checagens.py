import re
from collections.abc import Callable
from urllib.parse import urlsplit

from rastro.configuracao.modelos import Checagem, RegraDeChecagem, SituacaoDaChecagem
from rastro.har.modelos import Requisicao
from rastro.har.site import e_pagina_html, host_com_porta
from rastro.identificacao.modelos import Evidencia

CSP_AUSENTE = RegraDeChecagem("C01", "CSP ausente", "media", "infra")
HSTS_AUSENTE = RegraDeChecagem("C02", "HSTS ausente", "media", "infra")
NOSNIFF_AUSENTE = RegraDeChecagem("C03", "nosniff ausente", "baixa", "infra")
FRAME_SEM_PROTECAO = RegraDeChecagem("C04", "proteção contra frame ausente", "baixa", "infra")
SERVIDOR_EXPOE_VERSAO = RegraDeChecagem("C05", "servidor expõe versão", "baixa", "infra")

CABECALHOS_DE_SERVIDOR = ("server", "x-powered-by")
PADRAO_DE_VERSAO = re.compile(r"\d+\.\d+|/v?\d+")
SEPARADOR_DE_DIRETIVAS_CSP = re.compile(r"[;,]")

TesteDeFalha = Callable[[Requisicao], bool]
TrechoDaEvidencia = Callable[[Requisicao], str | None]


def checar_csp(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        CSP_AUSENTE,
        paginas_html_do_site(requisicoes, site),
        sem_csp,
        "a página não envia Content-Security-Policy",
    )


def checar_hsts(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    paginas = paginas_html_do_site(requisicoes, site)
    paginas_em_https = [pagina for pagina in paginas if usa_https(pagina)]
    if paginas and not paginas_em_https:
        return nao_verificada(HSTS_AUSENTE, "o site não usa HTTPS; HSTS só vale em HTTPS")
    return checar_paginas_do_site(
        HSTS_AUSENTE,
        paginas_em_https,
        sem_hsts,
        "a página em HTTPS não envia Strict-Transport-Security",
    )


def checar_nosniff(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        NOSNIFF_AUSENTE,
        paginas_html_do_site(requisicoes, site),
        sem_nosniff,
        "a página não envia X-Content-Type-Options: nosniff",
    )


def checar_protecao_contra_frame(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        FRAME_SEM_PROTECAO,
        paginas_html_do_site(requisicoes, site),
        sem_protecao_contra_frame,
        "a página não envia X-Frame-Options nem frame-ancestors na CSP",
    )


def checar_versao_do_servidor(requisicoes: list[Requisicao], site: str | None) -> Checagem:
    return checar_paginas_do_site(
        SERVIDOR_EXPOE_VERSAO,
        paginas_html_do_site(requisicoes, site),
        expoe_versao_do_servidor,
        "o cabeçalho mostra a versão do servidor",
        cabecalhos_com_versao,
    )


def paginas_html_do_site(requisicoes: list[Requisicao], site: str | None) -> list[Requisicao]:
    paginas = []
    for requisicao in requisicoes:
        if e_pagina_html(requisicao) and e_do_site(requisicao, site):
            paginas.append(requisicao)
    return paginas


def e_do_site(requisicao: Requisicao, site: str | None) -> bool:
    return site is not None and host_com_porta(requisicao.url) == site


def checar_paginas_do_site(
    regra: RegraDeChecagem,
    paginas: list[Requisicao],
    falha: TesteDeFalha,
    motivo_da_falha: str,
    trecho_da_evidencia: TrechoDaEvidencia | None = None,
) -> Checagem:
    if not paginas:
        return nao_verificada(regra, "nenhuma resposta HTML do site analisado no HAR")
    for pagina in paginas:
        if falha(pagina):
            trecho = None
            if trecho_da_evidencia is not None:
                trecho = trecho_da_evidencia(pagina)
            evidencia = Evidencia(pagina.indice, pagina.url, trecho)
            return montar_checagem(regra, "falhou", evidencia, f"{motivo_da_falha}: {pagina.url}")
    primeira = paginas[0]
    evidencia = Evidencia(primeira.indice, primeira.url, None)
    detalhe = f"as {len(paginas)} respostas HTML do site conferidas passaram"
    return montar_checagem(regra, "passou", evidencia, detalhe)


def montar_checagem(
    regra: RegraDeChecagem,
    situacao: SituacaoDaChecagem,
    evidencia: Evidencia,
    detalhe: str,
) -> Checagem:
    return Checagem(
        id=regra.id,
        titulo=regra.titulo,
        situacao=situacao,
        severidade=regra.severidade,
        quem_resolve=regra.quem_resolve,
        evidencia=evidencia,
        detalhe=detalhe,
    )


def nao_verificada(regra: RegraDeChecagem, detalhe: str) -> Checagem:
    return Checagem(
        id=regra.id,
        titulo=regra.titulo,
        situacao="nao_verificada",
        severidade=regra.severidade,
        quem_resolve=regra.quem_resolve,
        evidencia=None,
        detalhe=detalhe,
    )


def cabecalho(requisicao: Requisicao, nome: str) -> str:
    return requisicao.cabecalhos_resposta.get(nome, "").strip()


def usa_https(requisicao: Requisicao) -> bool:
    return urlsplit(requisicao.url).scheme.lower() == "https"


def sem_csp(pagina: Requisicao) -> bool:
    return not cabecalho(pagina, "content-security-policy")


def sem_hsts(pagina: Requisicao) -> bool:
    return not cabecalho(pagina, "strict-transport-security")


def sem_nosniff(pagina: Requisicao) -> bool:
    return cabecalho(pagina, "x-content-type-options").lower() != "nosniff"


def sem_protecao_contra_frame(pagina: Requisicao) -> bool:
    return not cabecalho(pagina, "x-frame-options") and not csp_tem_frame_ancestors(pagina)


def csp_tem_frame_ancestors(pagina: Requisicao) -> bool:
    politica = cabecalho(pagina, "content-security-policy")
    for diretiva in SEPARADOR_DE_DIRETIVAS_CSP.split(politica):
        nome_da_diretiva = diretiva.strip().split(" ")[0].lower()
        if nome_da_diretiva == "frame-ancestors":
            return True
    return False


def expoe_versao_do_servidor(pagina: Requisicao) -> bool:
    return cabecalhos_com_versao(pagina) is not None


def cabecalhos_com_versao(pagina: Requisicao) -> str | None:
    for nome in CABECALHOS_DE_SERVIDOR:
        valor = cabecalho(pagina, nome)
        if PADRAO_DE_VERSAO.search(valor):
            return f"{nome}: {valor}"
    return None
