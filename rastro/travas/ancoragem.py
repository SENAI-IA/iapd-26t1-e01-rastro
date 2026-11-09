import re
from dataclasses import replace

from rastro.identificacao.modelos import Biblioteca, Evidencia
from rastro.travas.modelos import TravaAcionada

TRAVA_TRECHO_REAL = "trecho real"
TRAVA_ANCORAGEM = "ancoragem"


def conferir_ancoragem(
    biblioteca: Biblioteca, trechos_enviados: list[str]
) -> tuple[Biblioteca, list[TravaAcionada]]:
    travas_acionadas = []
    for evidencia in biblioteca.evidencias:
        travas_acionadas.extend(conferir_evidencia(biblioteca, evidencia, trechos_enviados))
    if not biblioteca.evidencias:
        travas_acionadas.append(barrar_sem_evidencia(biblioteca))
    if not travas_acionadas:
        return biblioteca, []
    return mandar_para_a_confirmar(biblioteca, travas_acionadas), travas_acionadas


def conferir_evidencia(
    biblioteca: Biblioteca, evidencia: Evidencia, trechos_enviados: list[str]
) -> list[TravaAcionada]:
    alvo = nome_completo(biblioteca)
    trecho = evidencia.trecho or ""
    travas_acionadas = []
    if not trecho_foi_enviado(trecho, trechos_enviados):
        motivo = f"o trecho citado pela IA não está entre os trechos enviados de {evidencia.url}"
        travas_acionadas.append(TravaAcionada(TRAVA_TRECHO_REAL, alvo, motivo))
    if not versao_esta_no_trecho(biblioteca.versao, trecho):
        motivo = (
            f"a versão {biblioteca.versao} não aparece no trecho citado: "
            f"procure `{biblioteca.versao}` em {evidencia.url}"
        )
        travas_acionadas.append(TravaAcionada(TRAVA_ANCORAGEM, alvo, motivo))
    return travas_acionadas


def barrar_sem_evidencia(biblioteca: Biblioteca) -> TravaAcionada:
    return TravaAcionada(TRAVA_TRECHO_REAL, nome_completo(biblioteca), "a IA não citou trecho")


def trecho_foi_enviado(trecho: str, trechos_enviados: list[str]) -> bool:
    if not trecho.strip():
        return False
    return any(trecho in enviado for enviado in trechos_enviados)


def versao_esta_no_trecho(versao: str, trecho: str) -> bool:
    return padrao_da_versao_isolada(versao).search(trecho) is not None


def padrao_da_versao_isolada(versao: str) -> re.Pattern[str]:
    sem_numero_antes = r"(?<!\d)(?<!\d\.)"
    sem_continuacao_depois = r"(?!\d|\.\d|-[0-9A-Za-z])"
    return re.compile(sem_numero_antes + re.escape(versao) + sem_continuacao_depois)


def mandar_para_a_confirmar(
    biblioteca: Biblioteca, travas_acionadas: list[TravaAcionada]
) -> Biblioteca:
    travas_que_falharam = list(biblioteca.travas_que_falharam)
    for trava_acionada in travas_acionadas:
        if trava_acionada.trava not in travas_que_falharam:
            travas_que_falharam.append(trava_acionada.trava)
    return replace(biblioteca, situacao="a_confirmar", travas_que_falharam=travas_que_falharam)


def nome_completo(biblioteca: Biblioteca) -> str:
    return f"{biblioteca.pacote}@{biblioteca.versao}"
