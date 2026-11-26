from rastro.fontes.consulta_dos_avisos import AvisosDaBiblioteca
from rastro.identificacao.modelos import nome_com_versao
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


def agrupar_por_biblioteca(achados: list[Achado]) -> dict[str, list[Achado]]:
    grupos: dict[str, list[Achado]] = {}
    for achado in achados:
        if achado.biblioteca.situacao != "confirmada":
            continue
        grupos.setdefault(nome_com_versao(achado.biblioteca), []).append(achado)
    return grupos


def achados_da_biblioteca(chave: str, achados: list[Achado]) -> list[Achado]:
    return [achado for achado in achados if nome_com_versao(achado.biblioteca) == chave]
