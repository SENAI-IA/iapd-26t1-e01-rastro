import os
import sys
import webbrowser
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DESCRITOR_DA_SAIDA_PADRAO = 1
DESCRITOR_DA_SAIDA_DE_ERRO = 2
DESCRITORES_DAS_SAIDAS = (DESCRITOR_DA_SAIDA_PADRAO, DESCRITOR_DA_SAIDA_DE_ERRO)
TEXTO_RELATORIO_ABERTO = "Relatório aberto no navegador."
TEXTO_RELATORIO_SEM_NAVEGADOR = (
    "Não foi possível abrir o navegador. Abra o arquivo HTML acima nele para ver o relatório."
)


def abrir_arquivo_no_navegador(caminho: Path) -> bool:
    with avisos_do_navegador_fora_do_terminal():
        return webbrowser.open(caminho.resolve().as_uri())


@contextmanager
def avisos_do_navegador_fora_do_terminal() -> Iterator[None]:
    esvaziar_as_saidas()
    copias_das_saidas = guardar_copias_das_saidas()
    descritor_nulo = abrir_o_descarte()
    try:
        mandar_as_saidas_para(descritor_nulo)
        yield
    finally:
        devolver_as_saidas(copias_das_saidas)
        os.close(descritor_nulo)


def esvaziar_as_saidas() -> None:
    sys.stdout.flush()
    sys.stderr.flush()


def guardar_copias_das_saidas() -> dict[int, int]:
    copias = {}
    for descritor in DESCRITORES_DAS_SAIDAS:
        copias[descritor] = os.dup(descritor)
    return copias


def abrir_o_descarte() -> int:
    return os.open(os.devnull, os.O_WRONLY)


def mandar_as_saidas_para(descritor_de_destino: int) -> None:
    for descritor in DESCRITORES_DAS_SAIDAS:
        os.dup2(descritor_de_destino, descritor)


def devolver_as_saidas(copias_das_saidas: dict[int, int]) -> None:
    for descritor, copia_do_original in copias_das_saidas.items():
        os.dup2(copia_do_original, descritor)
        os.close(copia_do_original)


def abrir_relatorio(caminho_do_html: Path) -> None:
    if abrir_arquivo_no_navegador(caminho_do_html):
        print(TEXTO_RELATORIO_ABERTO)
    else:
        print(TEXTO_RELATORIO_SEM_NAVEGADOR)
