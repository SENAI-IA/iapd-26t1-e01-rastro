from dataclasses import asdict
from typing import Any

from rastro.acao.modelos import Acao
from rastro.acao.plano import chave_da_biblioteca
from rastro.configuracao.modelos import SituacaoDaChecagem
from rastro.fluxo import Analise
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado, Prioridade
from rastro.risco.prioridade import nota_da_biblioteca

VERSAO_FORMATO = 1
PRIORIDADES: tuple[Prioridade, ...] = ("alta", "media", "baixa", "a avaliar")

TEXTO_BUNDLES_NAO_PROCURADOS = (
    "Bibliotecas escondidas em bundles não foram procuradas: "
    "podem existir falhas que não aparecem aqui."
)
TEXTO_ACHADOS_SEM_EXPLICACAO = (
    "Os achados trazem o resumo do próprio aviso, "
    "sem explicação em linguagem simples nem teste de verificação."
)
TEXTO_CONTINUA_IGUAL_SEM_IA = (
    "A nota, a prioridade, as checagens e o plano de ação são os mesmos "
    "de uma análise com IA."
)
TEXTO_SEM_JAVASCRIPT = (
    "Nenhuma resposta do HAR trouxe conteúdo JavaScript, então nenhuma biblioteca pôde ser "
    "analisada. O HAR pode ter sido gravado sem o conteúdo das respostas, ou o site não "
    "carrega scripts. As checagens de cabeçalhos e cookies foram feitas."
)


def montar_relatorio(analise: Analise) -> dict[str, Any]:
    return {
        "versao_formato": VERSAO_FORMATO,
        "analise": dados_da_analise(analise),
        "resumo": montar_resumo(analise),
        "bibliotecas": [biblioteca_no_relatorio(b, analise) for b in analise.bibliotecas],
        "a_confirmar": [biblioteca_no_relatorio(b, analise) for b in analise.a_confirmar],
        "achados": [achado_no_relatorio(achado) for achado in analise.achados],
        "checagens": [asdict(checagem) for checagem in analise.checagens],
        "plano_de_acao": [asdict(acao) for acao in analise.plano_de_acao],
        "ia": dados_da_ia(analise),
    }


def dados_da_analise(analise: Analise) -> dict[str, Any]:
    return {
        "har": analise.har,
        "site": analise.site,
        "data": analise.inicio.isoformat(timespec="seconds"),
        "ia": analise.provedor_de_ia,
        "limitacoes": listar_limitacoes(analise),
        "continua_igual": continua_igual(analise),
        "duracao_s": analise.duracao_s,
    }


def listar_limitacoes(analise: Analise) -> list[dict[str, str]]:
    limitacoes = []
    if analise.provedor_de_ia is None:
        limitacoes.append(limitacao("bundles_nao_procurados", TEXTO_BUNDLES_NAO_PROCURADOS))
        limitacoes.append(limitacao("achados_sem_explicacao", TEXTO_ACHADOS_SEM_EXPLICACAO))
    if not analise.tem_javascript:
        limitacoes.append(limitacao("sem_javascript", TEXTO_SEM_JAVASCRIPT))
    return limitacoes


def limitacao(identificador: str, texto: str) -> dict[str, str]:
    return {"id": identificador, "texto": texto}


def continua_igual(analise: Analise) -> str | None:
    if analise.provedor_de_ia is None:
        return TEXTO_CONTINUA_IGUAL_SEM_IA
    return None


def montar_resumo(analise: Analise) -> dict[str, Any]:
    return {
        "nota_maxima": nota_da_biblioteca(analise.achados),
        "acoes": len(analise.plano_de_acao),
        "acoes_por_prioridade": contar_acoes_por_prioridade(analise.plano_de_acao),
        "bibliotecas": len(analise.bibliotecas),
        "bibliotecas_vulneraveis": len(chaves_das_bibliotecas_com_achados(analise.achados)),
        "bibliotecas_a_confirmar": len(analise.a_confirmar),
        "bibliotecas_nao_consultadas": len(analise.nao_consultadas),
        "achados": len(analise.achados),
        "checagens_com_falha": contar_checagens(analise, "falhou"),
        "checagens_nao_verificadas": contar_checagens(analise, "nao_verificada"),
        "encontradas_so_pela_ia": encontradas_so_pela_ia(analise),
    }


def contar_acoes_por_prioridade(acoes: list[Acao]) -> dict[str, int]:
    contagem: dict[str, int] = {prioridade: 0 for prioridade in PRIORIDADES}
    for acao in acoes:
        contagem[acao.prioridade] += 1
    return contagem


def chaves_das_bibliotecas_com_achados(achados: list[Achado]) -> set[str]:
    return {chave_da_biblioteca(achado.biblioteca) for achado in achados}


def contar_checagens(analise: Analise, situacao: SituacaoDaChecagem) -> int:
    return sum(1 for checagem in analise.checagens if checagem.situacao == situacao)


def encontradas_so_pela_ia(analise: Analise) -> int | None:
    if analise.provedor_de_ia is None:
        return None
    return sum(1 for biblioteca in analise.bibliotecas if biblioteca.metodo == "ia")


def biblioteca_no_relatorio(biblioteca: Biblioteca, analise: Analise) -> dict[str, Any]:
    chave = chave_da_biblioteca(biblioteca)
    achados = achados_da_biblioteca(chave, analise.achados)
    explicacao = analise.explicacoes.get(chave)
    return {
        "id": chave,
        **asdict(biblioteca),
        "nota": nota_da_biblioteca(achados),
        "achados": [achado.aviso.ghsa for achado in achados],
        "motivo_nao_consultada": analise.nao_consultadas.get(chave),
        "explicacao": asdict(explicacao) if explicacao is not None else None,
    }


def achados_da_biblioteca(chave: str, achados: list[Achado]) -> list[Achado]:
    return [achado for achado in achados if chave_da_biblioteca(achado.biblioteca) == chave]


def achado_no_relatorio(achado: Achado) -> dict[str, Any]:
    return {
        "biblioteca": chave_da_biblioteca(achado.biblioteca),
        "aviso": asdict(achado.aviso),
        "nota": asdict(achado.nota),
    }


def dados_da_ia(analise: Analise) -> dict[str, Any]:
    return {
        "chamadas": [],
        "travas_acionadas": [asdict(trava) for trava in analise.travas_acionadas],
        "com_e_sem_ia": None,
        "tokens_total": None,
    }
