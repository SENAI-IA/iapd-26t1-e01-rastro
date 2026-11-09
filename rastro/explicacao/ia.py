import json
from dataclasses import dataclass
from importlib import resources

from rastro.acao.plano import agrupar_por_biblioteca
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.conector import Aviso
from rastro.har.site import url_sem_query_string
from rastro.ia.cliente import ClienteDeIA
from rastro.ia.sanitizacao import sanitizar
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado
from rastro.risco.prioridade import ordenar_achados
from rastro.travas import formato
from rastro.travas.explicacao import conferir_explicacao
from rastro.travas.formato import (
    ForaDoFormato,
    exigir_campos,
    ler_json_sem_texto_fora,
    ler_texto,
    tirar_cerca_de_codigo,
)
from rastro.travas.modelos import TravaAcionada

ETAPA = "explicar_achado"
ARQUIVO_DO_PROMPT = "explicar_achado.md"
MARCADOR_DA_ENTRADA = "{{entrada}}"
CAMPOS_DA_EXPLICACAO = ("o_que_e", "impacto", "como_corrigir", "teste_verificacao")


@dataclass(frozen=True)
class ExplicacoesDosAchados:
    explicacoes: dict[str, Explicacao]
    travas_acionadas: list[TravaAcionada]


def explicar_achados(achados: list[Achado], ia: ClienteDeIA | None) -> ExplicacoesDosAchados:
    if ia is None:
        return ExplicacoesDosAchados({}, [])
    explicacoes: dict[str, Explicacao] = {}
    travas_acionadas: list[TravaAcionada] = []
    for chave, achados_da_biblioteca in agrupar_por_biblioteca(achados).items():
        explicacao, barrados = explicar_biblioteca(achados_da_biblioteca, ia)
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
    resposta = ia.perguntar(ETAPA, montar_prompt(entrada))
    if resposta is None:
        return sem_ia, []
    alvo = f"explicação de {biblioteca.pacote}@{biblioteca.versao}"
    try:
        campos = ler_campos_da_explicacao(resposta)
    except ForaDoFormato as erro:
        motivo = f"explicação descartada: {erro}"
        return sem_ia, [TravaAcionada(formato.NOME_DA_TRAVA, alvo, motivo)]
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


def montar_prompt(entrada: str) -> str:
    return ler_modelo_do_prompt().replace(MARCADOR_DA_ENTRADA, entrada)


def ler_modelo_do_prompt() -> str:
    prompts = resources.files("rastro.ia").joinpath("prompts")
    return prompts.joinpath(ARQUIVO_DO_PROMPT).read_text(encoding="utf-8")


def ler_campos_da_explicacao(resposta: str) -> dict[str, str]:
    objeto = ler_json_sem_texto_fora(tirar_cerca_de_codigo(resposta))
    campos = exigir_campos(objeto, set(CAMPOS_DA_EXPLICACAO), "na explicação")
    explicacao = {campo: ler_texto(campos, campo).strip() for campo in CAMPOS_DA_EXPLICACAO}
    vazios = [campo for campo, texto in explicacao.items() if not texto]
    if vazios:
        raise ForaDoFormato(f"campo vazio na explicação: {', '.join(vazios)}")
    return explicacao
