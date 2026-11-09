from dataclasses import dataclass, replace

from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.identificacao.modelos import Biblioteca
from rastro.travas.modelos import TravaAcionada

TRAVA_PACOTE_EXISTE = "pacote existe"


@dataclass(frozen=True)
class BibliotecasConferidas:
    confirmadas: list[Biblioteca]
    a_confirmar: list[Biblioteca]
    travas_acionadas: list[TravaAcionada]


def conferir_bibliotecas(
    bibliotecas: list[Biblioteca], registro: RegistroDePacotes
) -> BibliotecasConferidas:
    confirmadas = []
    a_confirmar = []
    travas_acionadas = []
    for biblioteca in bibliotecas:
        conferida, trava_acionada = conferir_pacote_no_npm(biblioteca, registro)
        if conferida.situacao == "confirmada":
            confirmadas.append(conferida)
        else:
            a_confirmar.append(conferida)
        if trava_acionada is not None:
            travas_acionadas.append(trava_acionada)
    return BibliotecasConferidas(confirmadas, a_confirmar, travas_acionadas)


def conferir_pacote_no_npm(
    biblioteca: Biblioteca, registro: RegistroDePacotes
) -> tuple[Biblioteca, TravaAcionada | None]:
    try:
        publicado = registro.existe(biblioteca.pacote, biblioteca.versao)
    except ConsultaNaoRealizada as erro:
        return conferir_sem_resposta_do_registro(biblioteca, erro.motivo)
    if publicado:
        return replace(biblioteca, conferida_no_npm=True), None
    motivo = f"{nome_completo(biblioteca)} não foi publicado no npm"
    return barrar(replace(biblioteca, conferida_no_npm=False), motivo)


def conferir_sem_resposta_do_registro(
    biblioteca: Biblioteca, motivo: str
) -> tuple[Biblioteca, TravaAcionada | None]:
    sem_conferencia = replace(biblioteca, conferida_no_npm=None)
    if biblioteca.metodo == "assinatura":
        return sem_conferencia, None
    return barrar(sem_conferencia, f"não foi possível conferir no npm: {motivo}")


def barrar(biblioteca: Biblioteca, motivo: str) -> tuple[Biblioteca, TravaAcionada]:
    barrada = replace(
        biblioteca,
        situacao="a_confirmar",
        travas_que_falharam=[*biblioteca.travas_que_falharam, TRAVA_PACOTE_EXISTE],
    )
    return barrada, TravaAcionada(TRAVA_PACOTE_EXISTE, nome_completo(biblioteca), motivo)


def nome_completo(biblioteca: Biblioteca) -> str:
    return f"{biblioteca.pacote}@{biblioteca.versao}"
