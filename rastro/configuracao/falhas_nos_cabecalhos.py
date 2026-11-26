import re

from rastro.har.modelos import Requisicao

CABECALHOS_DE_SERVIDOR = ("server", "x-powered-by")
PADRAO_DE_VERSAO = re.compile(r"\d+\.\d+|/v?\d+")
SEPARADOR_DE_DIRETIVAS_CSP = re.compile(r"[;,]")


def ler_cabecalho(requisicao: Requisicao, nome: str) -> str:
    return requisicao.cabecalhos_resposta.get(nome, "").strip()


def sem_csp(pagina: Requisicao) -> bool:
    return not ler_cabecalho(pagina, "content-security-policy")


def sem_hsts(pagina: Requisicao) -> bool:
    return not ler_cabecalho(pagina, "strict-transport-security")


def sem_nosniff(pagina: Requisicao) -> bool:
    return ler_cabecalho(pagina, "x-content-type-options").lower() != "nosniff"


def sem_protecao_contra_frame(pagina: Requisicao) -> bool:
    return not ler_cabecalho(pagina, "x-frame-options") and not csp_tem_frame_ancestors(pagina)


def csp_tem_frame_ancestors(pagina: Requisicao) -> bool:
    politica = ler_cabecalho(pagina, "content-security-policy")
    diretivas = SEPARADOR_DE_DIRETIVAS_CSP.split(politica)
    return any(diretiva_e_frame_ancestors(diretiva) for diretiva in diretivas)


def diretiva_e_frame_ancestors(diretiva: str) -> bool:
    nome_da_diretiva = diretiva.strip().split(" ")[0].lower()
    return nome_da_diretiva == "frame-ancestors"


def expoe_versao_do_servidor(pagina: Requisicao) -> bool:
    return cabecalho_que_mostra_versao(pagina) is not None


def cabecalho_que_mostra_versao(pagina: Requisicao) -> str | None:
    for nome in CABECALHOS_DE_SERVIDOR:
        valor = ler_cabecalho(pagina, nome)
        if PADRAO_DE_VERSAO.search(valor):
            return f"{nome}: {valor}"
    return None
