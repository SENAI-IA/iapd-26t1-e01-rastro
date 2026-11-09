from rastro.risco.modelos import Achado, Prioridade

NOTA_MINIMA_DA_ALTA = 7.5
NOTA_MINIMA_DA_MEDIA = 6.5


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
    cvss = achado.aviso.cvss
    sem_nota = nota is None
    nota_decrescente = -nota if nota is not None else 0.0
    cvss_decrescente = -cvss if cvss is not None else 0.0
    return (sem_nota, nota_decrescente, cvss_decrescente)
