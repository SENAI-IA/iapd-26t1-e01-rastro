from rastro.identificacao.modelos import Biblioteca, Evidencia, nome_com_versao
from rastro.travas.marcacao_a_confirmar import mandar_para_a_confirmar
from rastro.travas.modelos import TravaAcionada
from rastro.travas.versao_no_trecho import versao_esta_no_trecho

TRAVA_TRECHO_REAL = "trecho real"
TRAVA_ANCORAGEM = "ancoragem"


def conferir_ancoragem(
    biblioteca: Biblioteca, trechos_enviados: list[str]
) -> tuple[Biblioteca, list[TravaAcionada]]:
    travas_acionadas = []
    for evidencia in biblioteca.evidencias:
        travas_acionadas.extend(
            conferir_evidencia_nos_trechos_enviados(biblioteca, evidencia, trechos_enviados)
        )
    if not biblioteca.evidencias:
        travas_acionadas.append(barrar_sem_evidencia(biblioteca))
    if not travas_acionadas:
        return biblioteca, []
    return mandar_para_a_confirmar(biblioteca, travas_acionadas), travas_acionadas


def conferir_evidencia_nos_trechos_enviados(
    biblioteca: Biblioteca, evidencia: Evidencia, trechos_enviados: list[str]
) -> list[TravaAcionada]:
    alvo = nome_com_versao(biblioteca)
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
    return TravaAcionada(TRAVA_TRECHO_REAL, nome_com_versao(biblioteca), "a IA não citou trecho")


def trecho_foi_enviado(trecho: str, trechos_enviados: list[str]) -> bool:
    if not trecho.strip():
        return False
    return any(trecho in enviado for enviado in trechos_enviados)
