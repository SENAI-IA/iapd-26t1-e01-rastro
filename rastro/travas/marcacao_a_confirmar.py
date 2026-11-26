from dataclasses import replace

from rastro.identificacao.modelos import Biblioteca
from rastro.travas.modelos import TravaAcionada


def mandar_para_a_confirmar(
    biblioteca: Biblioteca, travas_acionadas: list[TravaAcionada]
) -> Biblioteca:
    travas_que_falharam = list(biblioteca.travas_que_falharam)
    for trava_acionada in travas_acionadas:
        if trava_acionada.trava not in travas_que_falharam:
            travas_que_falharam.append(trava_acionada.trava)
    return replace(biblioteca, situacao="a_confirmar", travas_que_falharam=travas_que_falharam)
