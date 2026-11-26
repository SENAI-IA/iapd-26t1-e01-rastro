from dataclasses import dataclass

EventoSemver = dict[str, str]
INICIO_DE_TODAS_AS_VERSOES = "0"
CONDICAO_DE_TODAS_AS_VERSOES = ">= 0"


@dataclass(frozen=True)
class FaixaSemver:
    faixa: str
    versao_corrigida: str | None


def faixas_dos_eventos_semver(eventos: list[EventoSemver]) -> list[FaixaSemver]:
    faixas = []
    inicio: str | None = None
    for evento in eventos:
        if "introduced" in evento:
            inicio = evento["introduced"]
        elif inicio is not None and fecha_a_faixa(evento):
            faixas.append(faixa_fechada(inicio, evento))
            inicio = None
    if inicio is not None:
        faixas.append(FaixaSemver(faixa_aberta(inicio), None))
    return faixas


def fecha_a_faixa(evento: EventoSemver) -> bool:
    return "fixed" in evento or "last_affected" in evento


def faixa_fechada(inicio: str, evento: EventoSemver) -> FaixaSemver:
    fim, versao_corrigida = fim_da_faixa_e_versao_corrigida(evento)
    condicoes = []
    inicio_da_faixa = condicao_de_inicio(inicio)
    if inicio_da_faixa:
        condicoes.append(inicio_da_faixa)
    condicoes.append(fim)
    return FaixaSemver(", ".join(condicoes), versao_corrigida)


def fim_da_faixa_e_versao_corrigida(evento: EventoSemver) -> tuple[str, str | None]:
    if "fixed" in evento:
        return f"< {evento['fixed']}", evento["fixed"]
    return f"<= {evento['last_affected']}", None


def faixa_aberta(inicio: str) -> str:
    inicio_da_faixa = condicao_de_inicio(inicio)
    if not inicio_da_faixa:
        return CONDICAO_DE_TODAS_AS_VERSOES
    return inicio_da_faixa


def condicao_de_inicio(inicio: str) -> str:
    if inicio == INICIO_DE_TODAS_AS_VERSOES:
        return ""
    return f">= {inicio}"
