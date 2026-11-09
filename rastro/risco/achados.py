from rastro.fontes.consulta import AvisosDaBiblioteca
from rastro.risco.modelos import Achado
from rastro.risco.nota import calcular_nota
from rastro.risco.prioridade import ordenar_achados


def calcular_risco(avisos: list[AvisosDaBiblioteca]) -> list[Achado]:
    achados = []
    for biblioteca, avisos_da_biblioteca in avisos:
        for aviso in avisos_da_biblioteca:
            nota = calcular_nota(aviso.cvss, aviso.percentil_epss)
            achados.append(Achado(biblioteca, aviso, nota))
    return ordenar_achados(achados)
