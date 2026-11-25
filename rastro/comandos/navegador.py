import os
import sys
import webbrowser
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

TEXTO_RELATORIO_ABERTO = "Relatório aberto no navegador."
TEXTO_RELATORIO_SEM_NAVEGADOR = (
    "Não foi possível abrir o navegador. Abra o arquivo HTML acima nele para ver o relatório."
)


def abrir_no_navegador(caminho: Path) -> bool:
    with saida_do_terminal_silenciada():
        return webbrowser.open(caminho.resolve().as_uri())


@contextmanager
def saida_do_terminal_silenciada() -> Iterator[None]:
    """Manda para o nada o que o navegador escreve no terminal.

    O navegador herda o terminal de quem o abre e, já aberto, escreve avisos
    como "Abrindo em uma sessão de navegador existente." e erros internos do Chrome.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    originais = [(descritor, os.dup(descritor)) for descritor in (1, 2)]
    nada = os.open(os.devnull, os.O_WRONLY)
    try:
        for descritor, _ in originais:
            os.dup2(nada, descritor)
        yield
    finally:
        for descritor, original in originais:
            os.dup2(original, descritor)
            os.close(original)
        os.close(nada)


def abrir_relatorio(html: Path) -> None:
    if abrir_no_navegador(html):
        print(TEXTO_RELATORIO_ABERTO)
    else:
        print(TEXTO_RELATORIO_SEM_NAVEGADOR)
