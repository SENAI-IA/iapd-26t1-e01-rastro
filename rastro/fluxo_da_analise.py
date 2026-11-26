import time
from datetime import datetime
from pathlib import Path

from rastro.acao.plano_de_acao import montar_plano_de_acao
from rastro.andamento import ANDAMENTO_SILENCIOSO, Andamento
from rastro.configuracao.checagens import checar_configuracao
from rastro.explicacao.explicacao_dos_achados import explicar_achados
from rastro.fontes.completar_cvss import BuscaDeCvss
from rastro.fontes.conector import ConectorDeAvisos
from rastro.fontes.consulta_dos_avisos import consultar_avisos
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.har.leitor_do_har import ler_har
from rastro.har.site import descobrir_site_analisado
from rastro.har.visita import montar_visita
from rastro.ia.cliente import ChamadaDaIA, ClienteDeIA
from rastro.identificacao.assinaturas import algum_script_com_conteudo, identificar_por_assinatura
from rastro.identificacao.bibliotecas_pela_ia import identificar_em_bundles
from rastro.modelos_da_analise import Analise
from rastro.risco.achados import calcular_risco
from rastro.travas.conferencia_das_bibliotecas import conferir_bibliotecas
from rastro.travas.faixa_de_versao import conferir_faixas

ETAPA_LER_O_HAR = "Lendo o HAR"
ETAPA_RECONHECER = "Reconhecendo as bibliotecas pelos arquivos"
ETAPA_BUNDLES = "Procurando bibliotecas nos bundles com a IA"
ETAPA_CONFERIR = "Conferindo as bibliotecas no npm"
ETAPA_CONSULTAR = "Consultando falhas conhecidas (GitHub, OSV, NVD)"
ETAPA_EXPLICAR = "Explicando os achados com a IA"
ETAPA_PLANO = "Conferindo a configuração e montando o plano de ação"
ETAPAS_SEM_IA = 5
ETAPAS_COM_IA = 7


def analisar(
    caminho_har: Path,
    fonte: ConectorDeAvisos,
    registro: RegistroDePacotes,
    cliente_de_ia: ClienteDeIA | None = None,
    conector_osv: ConectorDeAvisos | None = None,
    busca_de_cvss: BuscaDeCvss | None = None,
    gravado_pelo_rastro: bool = False,
    andamento: Andamento = ANDAMENTO_SILENCIOSO,
) -> Analise:
    inicio = datetime.now()
    inicio_do_cronometro = time.perf_counter()
    andamento.comecar_analise(ETAPAS_SEM_IA if cliente_de_ia is None else ETAPAS_COM_IA)

    andamento.iniciar_etapa(ETAPA_LER_O_HAR)
    requisicoes = ler_har(caminho_har)
    site = descobrir_site_analisado(requisicoes)
    andamento.iniciar_etapa(ETAPA_RECONHECER)
    bibliotecas_por_assinatura = identificar_por_assinatura(requisicoes)
    if cliente_de_ia is not None:
        andamento.iniciar_etapa(ETAPA_BUNDLES)
    resultado_dos_bundles = identificar_em_bundles(
        requisicoes, bibliotecas_por_assinatura, cliente_de_ia, andamento
    )
    andamento.iniciar_etapa(ETAPA_CONFERIR)
    bibliotecas = conferir_bibliotecas(
        bibliotecas_por_assinatura + resultado_dos_bundles.bibliotecas, registro, andamento
    )
    andamento.iniciar_etapa(ETAPA_CONSULTAR)
    consulta_de_avisos = consultar_avisos(
        bibliotecas.confirmadas, fonte, conector_osv, busca_de_cvss, andamento
    )
    avisos_na_faixa, travas_da_faixa = conferir_faixas(consulta_de_avisos.avisos)
    achados = calcular_risco(avisos_na_faixa)
    if cliente_de_ia is not None:
        andamento.iniciar_etapa(ETAPA_EXPLICAR)
    resultado_das_explicacoes = explicar_achados(achados, cliente_de_ia, andamento)
    andamento.iniciar_etapa(ETAPA_PLANO)
    checagens = checar_configuracao(requisicoes, site, gravado_pelo_rastro)
    plano_de_acao = montar_plano_de_acao(achados, resultado_das_explicacoes.explicacoes, checagens)

    return Analise(
        har=caminho_har.name,
        site=site,
        inicio=inicio,
        duracao_s=round(time.perf_counter() - inicio_do_cronometro, 1),
        provedor_de_ia=nome_do_provedor(cliente_de_ia),
        tem_javascript=algum_script_com_conteudo(requisicoes),
        bibliotecas=bibliotecas.confirmadas,
        a_confirmar=bibliotecas.a_confirmar,
        nao_consultadas=consulta_de_avisos.nao_consultadas,
        fontes_sem_resposta=consulta_de_avisos.fontes_sem_resposta,
        achados=achados,
        explicacoes=resultado_das_explicacoes.explicacoes,
        checagens=checagens,
        plano_de_acao=plano_de_acao,
        travas_acionadas=(
            resultado_dos_bundles.travas_acionadas
            + bibliotecas.travas_acionadas
            + travas_da_faixa
            + resultado_das_explicacoes.travas_acionadas
        ),
        chamadas_de_ia=chamadas_feitas(cliente_de_ia),
        visita=montar_visita(requisicoes),
    )


def nome_do_provedor(cliente_de_ia: ClienteDeIA | None) -> str | None:
    if cliente_de_ia is None:
        return None
    return cliente_de_ia.provedor.nome


def chamadas_feitas(cliente_de_ia: ClienteDeIA | None) -> list[ChamadaDaIA]:
    if cliente_de_ia is None:
        return []
    return list(cliente_de_ia.chamadas)
