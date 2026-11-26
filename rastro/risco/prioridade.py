from rastro.risco.modelos import Achado, Prioridade

NOTA_MINIMA_DA_ALTA = 7.5
NOTA_MINIMA_DA_MEDIA = 6.5

PRIORIDADES: tuple[Prioridade, ...] = ("alta", "media", "baixa", "a avaliar")
ORDEM_DA_PRIORIDADE: dict[Prioridade, int] = {"alta": 0, "media": 1, "baixa": 2, "a avaliar": 3}
ROTULO_DA_PRIORIDADE: dict[Prioridade, str] = {
    "alta": "alta",
    "media": "média",
    "baixa": "baixa",
    "a avaliar": "a avaliar",
}


def classificar_prioridade(nota: float | None) -> Prioridade:
    if nota is None:
        return "a avaliar"
    if nota >= NOTA_MINIMA_DA_ALTA:
        return "alta"
    if nota >= NOTA_MINIMA_DA_MEDIA:
        return "media"
    return "baixa"


def nota_da_biblioteca(achados_da_biblioteca: list[Achado]) -> float | None:
    notas = [achado.nota.valor for achado in achados_da_biblioteca]
    notas_calculadas = [nota for nota in notas if nota is not None]
    if not notas_calculadas:
        return None
    return max(notas_calculadas)


def ordenar_achados(achados: list[Achado]) -> list[Achado]:
    return sorted(achados, key=chave_da_ordem)


def chave_da_ordem(achado: Achado) -> tuple[bool, float, float]:
    nota = achado.nota.valor
    sem_nota = nota is None
    nota_decrescente = valor_para_ordem_decrescente(nota)
    cvss_decrescente = valor_para_ordem_decrescente(achado.aviso.cvss)
    return (sem_nota, nota_decrescente, cvss_decrescente)


def valor_para_ordem_decrescente(valor: float | None) -> float:
    if valor is None:
        return 0.0
    return -valor
