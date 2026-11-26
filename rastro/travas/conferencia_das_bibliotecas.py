from dataclasses import dataclass

from rastro.andamento import SEM_ANDAMENTO, Andamento
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.identificacao.modelos import Biblioteca
from rastro.travas.codigo_publicado import conferir_codigo_publicado
from rastro.travas.modelos import TravaAcionada
from rastro.travas.pacote_existe import conferir_pacote_no_npm


@dataclass(frozen=True)
class BibliotecasConferidas:
    confirmadas: list[Biblioteca]
    a_confirmar: list[Biblioteca]
    travas_acionadas: list[TravaAcionada]


def conferir_bibliotecas(
    bibliotecas: list[Biblioteca],
    registro: RegistroDePacotes,
    andamento: Andamento = SEM_ANDAMENTO,
) -> BibliotecasConferidas:
    confirmadas = []
    a_confirmar = []
    travas_acionadas = []
    andamento.itens(len(bibliotecas))
    for biblioteca in bibliotecas:
        conferida, barrados = conferir_biblioteca(biblioteca, registro)
        andamento.avancar()
        if conferida.situacao == "confirmada":
            confirmadas.append(conferida)
        else:
            a_confirmar.append(conferida)
        travas_acionadas.extend(barrados)
    return BibliotecasConferidas(confirmadas, a_confirmar, travas_acionadas)


def conferir_biblioteca(
    biblioteca: Biblioteca, registro: RegistroDePacotes
) -> tuple[Biblioteca, list[TravaAcionada]]:
    if biblioteca.situacao == "a_confirmar":
        return biblioteca, []
    conferida, trava_acionada = conferir_pacote_no_npm(biblioteca, registro)
    if trava_acionada is not None:
        return conferida, [trava_acionada]
    if conferida.metodo == "ia":
        return conferir_codigo_publicado(conferida, registro)
    return conferida, []
