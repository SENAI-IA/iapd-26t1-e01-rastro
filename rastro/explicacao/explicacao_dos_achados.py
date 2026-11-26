import json
from dataclasses import dataclass

from rastro.andamento import SEM_ANDAMENTO, Andamento
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.modelos import Aviso
from rastro.har.site import url_sem_query_string
from rastro.ia.cliente import ClienteDeIA
from rastro.ia.montagem_do_prompt import montar_prompt
from rastro.ia.sanitizacao import sanitizar
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.achados import agrupar_por_biblioteca
from rastro.risco.modelos import Achado
from rastro.risco.prioridade import ordenar_achados
from rastro.travas.explicacao_sem_fato_novo import conferir_explicacao
from rastro.travas.formato_da_explicacao import conferir_formato_da_explicacao
from rastro.travas.modelos import TravaAcionada

ETAPA = "explicar_achado"
ARQUIVO_DO_PROMPT = "explicar_achado.md"


@dataclass(frozen=True)
class ExplicacoesDosAchados:
    explicacoes: dict[str, Explicacao]
    travas_acionadas: list[TravaAcionada]


def explicar_achados(
    achados: list[Achado], ia: ClienteDeIA | None, andamento: Andamento = SEM_ANDAMENTO
) -> ExplicacoesDosAchados:
    if ia is None:
        return ExplicacoesDosAchados({}, [])
    explicacoes: dict[str, Explicacao] = {}
    travas_acionadas: list[TravaAcionada] = []
    por_biblioteca = agrupar_por_biblioteca(achados)
    andamento.itens(len(por_biblioteca))
    for chave, achados_da_biblioteca in por_biblioteca.items():
        explicacao, barrados = explicar_biblioteca(achados_da_biblioteca, ia)
        andamento.avancar()
        explicacoes[chave] = explicacao
        travas_acionadas.extend(barrados)
    return ExplicacoesDosAchados(explicacoes, travas_acionadas)


def explicar_biblioteca(
    achados: list[Achado], ia: ClienteDeIA
) -> tuple[Explicacao, list[TravaAcionada]]:
    em_ordem = ordenar_achados(achados)
    biblioteca = em_ordem[0].biblioteca
    avisos = [achado.aviso for achado in em_ordem]
    sem_ia = explicacao_pelo_resumo(avisos[0])
    entrada = sanitizar(montar_entrada(biblioteca, avisos))
    resposta = ia.perguntar(ETAPA, montar_prompt(ARQUIVO_DO_PROMPT, entrada))
    if resposta is None:
        return sem_ia, []
    alvo = f"explicação de {biblioteca.pacote}@{biblioteca.versao}"
    campos, barrados = conferir_formato_da_explicacao(resposta, alvo)
    if campos is None:
        return sem_ia, barrados
    conferida, barrados = conferir_explicacao(biblioteca.pacote, biblioteca.versao, campos, entrada)
    if conferida is None:
        return sem_ia, barrados
    return Explicacao(**conferida, gerada_por_ia=True), []


def explicacao_pelo_resumo(aviso: Aviso) -> Explicacao:
    return Explicacao(
        o_que_e=aviso.resumo,
        impacto=aviso.resumo,
        como_corrigir="",
        teste_verificacao="",
        gerada_por_ia=False,
    )


def montar_entrada(biblioteca: Biblioteca, avisos: list[Aviso]) -> str:
    entrada = {
        "pacote": biblioteca.pacote,
        "versao": biblioteca.versao,
        "url_do_script": url_do_script(biblioteca),
        "avisos": [aviso_na_entrada(aviso) for aviso in avisos],
    }
    return json.dumps(entrada, ensure_ascii=False, indent=2)


def url_do_script(biblioteca: Biblioteca) -> str | None:
    if not biblioteca.evidencias:
        return None
    return url_sem_query_string(biblioteca.evidencias[0].url)


def aviso_na_entrada(aviso: Aviso) -> dict[str, object]:
    return {
        "ids": [aviso.ghsa] + ([aviso.cve] if aviso.cve else []),
        "resumo": aviso.resumo,
        "versoes_afetadas": aviso.versoes_afetadas,
        "versao_corrigida": aviso.versao_corrigida,
    }
