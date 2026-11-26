from rastro.fontes.modelos import FonteSemResposta
from rastro.modelos_da_analise import Analise

TEXTO_BUNDLES_NAO_PROCURADOS = (
    "Bibliotecas escondidas em bundles não foram procuradas: "
    "podem existir falhas que não aparecem aqui."
)
TEXTO_ACHADOS_SEM_EXPLICACAO = (
    "Os achados trazem o resumo do próprio aviso, "
    "sem explicação em linguagem simples nem teste de verificação."
)
TEXTO_CONTINUA_IGUAL_SEM_IA = (
    "A nota, a prioridade, as checagens e o plano de ação são os mesmos de uma análise com IA."
)
TEXTO_SEM_JAVASCRIPT = (
    "Nenhuma resposta do HAR trouxe conteúdo JavaScript, então nenhuma biblioteca pôde ser "
    "analisada. O HAR pode ter sido exportado com um filtro na aba Rede (como Fetch/XHR), "
    "que deixa os scripts fora do arquivo, ou gravado com o cache ligado, que grava os "
    "scripts sem o conteúdo. Também pode ser que o site não carregue scripts. Grave de novo "
    "com o filtro em Todos e o cache desativado. As checagens de cabeçalhos e cookies foram "
    "feitas."
)
CONSEQUENCIA_DA_IA_QUE_FALHOU = {
    "identificar_bibliotecas": (
        "ia_falhou_identificacao",
        "procurar bibliotecas em bundles: esses bundles ficaram sem análise e podem "
        "esconder falhas que não aparecem aqui.",
    ),
    "explicar_achado": (
        "ia_falhou_explicacao",
        "explicar achados: esses achados trazem só o resumo do próprio aviso.",
    ),
}
CONSEQUENCIA_DA_FONTE_SEM_RESPOSTA = {
    "OSV": "Esses avisos vêm só do GitHub Advisory.",
    "NVD": "Esses avisos seguem sem o CVSS do NVD.",
}


def listar_limitacoes(analise: Analise) -> list[dict[str, str]]:
    limitacoes = []
    if analise.provedor_de_ia is None:
        limitacoes.append(limitacao("bundles_nao_procurados", TEXTO_BUNDLES_NAO_PROCURADOS))
        limitacoes.append(limitacao("achados_sem_explicacao", TEXTO_ACHADOS_SEM_EXPLICACAO))
    if not analise.tem_javascript:
        limitacoes.append(limitacao("sem_javascript", TEXTO_SEM_JAVASCRIPT))
    limitacoes.extend(limitacoes_da_ia_que_falhou(analise))
    for fonte in fontes_que_nao_responderam(analise.fontes_sem_resposta):
        texto = texto_da_fonte_sem_resposta(fonte, analise.fontes_sem_resposta)
        limitacoes.append(limitacao(f"fonte_sem_resposta_{fonte.lower()}", texto))
    return limitacoes


def limitacoes_da_ia_que_falhou(analise: Analise) -> list[dict[str, str]]:
    limitacoes = []
    for etapa, (identificador, consequencia) in CONSEQUENCIA_DA_IA_QUE_FALHOU.items():
        chamadas = [chamada for chamada in analise.chamadas_de_ia if chamada.etapa == etapa]
        falhas = [chamada for chamada in chamadas if not chamada.sucesso]
        if falhas:
            texto = (
                f"A IA ({analise.provedor_de_ia}) falhou em {len(falhas)} de {len(chamadas)} "
                f"chamadas para {consequencia} O motivo está no painel da IA."
            )
            limitacoes.append(limitacao(identificador, texto))
    return limitacoes


def fontes_que_nao_responderam(sem_resposta: list[FonteSemResposta]) -> list[str]:
    return list(dict.fromkeys(item.fonte for item in sem_resposta))


def texto_da_fonte_sem_resposta(fonte: str, sem_resposta: list[FonteSemResposta]) -> str:
    alvos = "; ".join(f"{item.alvo}: {item.motivo}" for item in sem_resposta if item.fonte == fonte)
    return f"O {fonte} não respondeu ({alvos}). {CONSEQUENCIA_DA_FONTE_SEM_RESPOSTA[fonte]}"


def limitacao(identificador: str, texto: str) -> dict[str, str]:
    return {"id": identificador, "texto": texto}


def continua_igual(analise: Analise) -> str | None:
    if analise.provedor_de_ia is None:
        return TEXTO_CONTINUA_IGUAL_SEM_IA
    return None
