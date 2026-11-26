from dataclasses import replace

from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.identificacao.modelos import Biblioteca, nome_com_versao
from rastro.travas.modelos import TravaAcionada

TRAVA_PACOTE_EXISTE = "pacote existe"


def conferir_pacote_no_npm(
    biblioteca: Biblioteca, registro: RegistroDePacotes
) -> tuple[Biblioteca, TravaAcionada | None]:
    try:
        publicado = registro.existe(biblioteca.pacote, biblioteca.versao)
    except ConsultaNaoRealizada as erro:
        return conferir_sem_resposta_do_registro(biblioteca, erro.motivo)
    if publicado:
        return replace(biblioteca, conferida_no_npm=True), None
    motivo = f"{nome_com_versao(biblioteca)} não foi publicado no npm"
    return barrar_pacote_inexistente(replace(biblioteca, conferida_no_npm=False), motivo)


def conferir_sem_resposta_do_registro(
    biblioteca: Biblioteca, motivo: str
) -> tuple[Biblioteca, TravaAcionada | None]:
    sem_conferencia = replace(biblioteca, conferida_no_npm=None)
    if biblioteca.metodo == "assinatura":
        return sem_conferencia, None
    return barrar_pacote_inexistente(sem_conferencia, f"não foi possível conferir no npm: {motivo}")


def barrar_pacote_inexistente(
    biblioteca: Biblioteca, motivo: str
) -> tuple[Biblioteca, TravaAcionada]:
    barrada = replace(
        biblioteca,
        situacao="a_confirmar",
        travas_que_falharam=biblioteca.travas_que_falharam + [TRAVA_PACOTE_EXISTE],
    )
    return barrada, TravaAcionada(TRAVA_PACOTE_EXISTE, nome_com_versao(biblioteca), motivo)
