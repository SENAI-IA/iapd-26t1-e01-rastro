from rastro.travas.json_estrito import (
    TRAVA_FORMATO_FECHADO,
    ForaDoFormato,
    exigir_campos,
    ler_json_sem_texto_fora,
    ler_texto,
    tirar_cerca_de_codigo,
)
from rastro.travas.modelos import TravaAcionada

CAMPOS_DA_EXPLICACAO = ("o_que_e", "impacto", "como_corrigir", "teste_verificacao")


def conferir_formato_da_explicacao(
    resposta: str, alvo: str
) -> tuple[dict[str, str] | None, list[TravaAcionada]]:
    try:
        return ler_campos_da_explicacao(resposta), []
    except ForaDoFormato as erro:
        motivo = f"explicação descartada: {erro}"
        return None, [TravaAcionada(TRAVA_FORMATO_FECHADO, alvo, motivo)]


def ler_campos_da_explicacao(resposta: str) -> dict[str, str]:
    objeto = ler_json_sem_texto_fora(tirar_cerca_de_codigo(resposta))
    campos = exigir_campos(objeto, set(CAMPOS_DA_EXPLICACAO), "na explicação")
    explicacao = {campo: ler_texto(campos, campo).strip() for campo in CAMPOS_DA_EXPLICACAO}
    vazios = [campo for campo, texto in explicacao.items() if not texto]
    if vazios:
        raise ForaDoFormato(f"campo vazio na explicação: {', '.join(vazios)}")
    return explicacao
