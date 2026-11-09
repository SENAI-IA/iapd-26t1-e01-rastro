from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

PESO_DO_CVSS = Decimal("0.5")
PESO_DO_EPSS = Decimal("0.5")
UMA_CASA_DECIMAL = Decimal("0.1")


@dataclass(frozen=True)
class Nota:
    valor: float | None
    conta: str
    sem_epss: bool


def calcular_nota(cvss: float | None, percentil_epss: float | None) -> Nota:
    if cvss is None:
        return Nota(valor=None, conta="sem CVSS: sem nota", sem_epss=percentil_epss is None)
    if percentil_epss is None:
        return Nota(valor=cvss, conta=conta_sem_epss(cvss), sem_epss=True)
    nota = calcular_nota_de_risco(cvss, percentil_epss)
    return Nota(valor=nota, conta=conta_da_formula(cvss, percentil_epss, nota), sem_epss=False)


def calcular_nota_de_risco(cvss: float, percentil_epss: float) -> float:
    parte_do_cvss = PESO_DO_CVSS * Decimal(str(cvss)) / 10
    parte_do_epss = PESO_DO_EPSS * Decimal(str(percentil_epss))
    nota = 10 * (parte_do_cvss + parte_do_epss)
    return float(nota.quantize(UMA_CASA_DECIMAL, rounding=ROUND_HALF_UP))


def conta_da_formula(cvss: float, percentil_epss: float, nota: float) -> str:
    return (
        f"10 × ({escrever(PESO_DO_CVSS)} × {escrever_nota(cvss)}/10"
        f" + {escrever(PESO_DO_EPSS)} × {escrever(percentil_epss)}) = {escrever_nota(nota)}"
    )


def conta_sem_epss(cvss: float) -> str:
    return f"sem EPSS: nota = CVSS = {escrever_nota(cvss)}"


def escrever_nota(valor: float) -> str:
    return f"{valor:.1f}".replace(".", ",")


def escrever(valor: float | Decimal) -> str:
    return f"{Decimal(str(valor)).normalize():f}".replace(".", ",")
