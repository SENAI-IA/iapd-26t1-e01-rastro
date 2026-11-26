import os
import sys
import webbrowser
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DESCRITOR_DA_SAIDA_PADRAO = 1
DESCRITOR_DA_SAIDA_DE_ERRO = 2
TEXTO_RELATORIO_ABERTO = "Relatório aberto no navegador."
TEXTO_RELATORIO_SEM_NAVEGADOR = (
    "Não foi possível abrir o navegador. Abra o arquivo HTML acima nele para ver o relatório."
)


def abrir_arquivo_no_navegador(caminho: Path) -> bool:
    with avisos_do_navegador_fora_do_terminal():
        return webbrowser.open(caminho.resolve().as_uri())


@contextmanager
def avisos_do_navegador_fora_do_terminal() -> Iterator[None]:
    sys.stdout.flush()
    sys.stderr.flush()
    descritores = (DESCRITOR_DA_SAIDA_PADRAO, DESCRITOR_DA_SAIDA_DE_ERRO)
    copias_dos_originais = [(descritor, os.dup(descritor)) for descritor in descritores]
    descritor_nulo = os.open(os.devnull, os.O_WRONLY)
    try:
        for descritor, _ in copias_dos_originais:
            os.dup2(descritor_nulo, descritor)
        yield
    finally:
        for descritor, copia_do_original in copias_dos_originais:
            os.dup2(copia_do_original, descritor)
            os.close(copia_do_original)
        os.close(descritor_nulo)


def abrir_relatorio(caminho_do_html: Path) -> None:
    if abrir_arquivo_no_navegador(caminho_do_html):
        print(TEXTO_RELATORIO_ABERTO)
    else:
        print(TEXTO_RELATORIO_SEM_NAVEGADOR)
