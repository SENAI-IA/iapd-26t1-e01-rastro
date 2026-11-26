from dataclasses import dataclass

EventoSemver = dict[str, str]
INICIO_DE_TODAS_AS_VERSOES = "0"


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
        faixas.append(FaixaSemver(condicao_de_inicio(inicio) or ">= 0", None))
    return faixas


def fecha_a_faixa(evento: EventoSemver) -> bool:
    return "fixed" in evento or "last_affected" in evento


def faixa_fechada(inicio: str, evento: EventoSemver) -> FaixaSemver:
    if "fixed" in evento:
        fim, versao_corrigida = f"< {evento['fixed']}", evento["fixed"]
    else:
        fim, versao_corrigida = f"<= {evento['last_affected']}", None
    condicoes = [condicao for condicao in (condicao_de_inicio(inicio), fim) if condicao]
    return FaixaSemver(", ".join(condicoes), versao_corrigida)


def condicao_de_inicio(inicio: str) -> str:
    if inicio == INICIO_DE_TODAS_AS_VERSOES:
        return ""
    return f">= {inicio}"
