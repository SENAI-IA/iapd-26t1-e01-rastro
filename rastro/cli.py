import sys
from argparse import Namespace
from collections.abc import Callable

from rastro.comandos.argumentos import criar_leitor_de_argumentos
from rastro.comandos.comando_analisar import analisar_com_ia, analisar_sem_ia
from rastro.comandos.comando_como_usar import abrir_como_usar
from rastro.comandos.comando_desinstalar import executar_comando_desinstalar
from rastro.comandos.comando_gravar import gravar_e_analisar
from rastro.comandos.comando_instalar import executar_comando_instalar
from rastro.comandos.comando_pentest import executar_comando_pentest


def principal() -> None:
    sys.exit(executar())


def executar(argumentos: list[str] | None = None) -> int:
    leitor_de_argumentos = criar_leitor_de_argumentos()
    opcoes = leitor_de_argumentos.parse_args(argumentos)
    if opcoes.comando is None:
        leitor_de_argumentos.print_help()
        return 0
    executar_comando = COMANDO_PELO_NOME[opcoes.comando]
    return executar_comando(opcoes)


def rodar_como_usar(_opcoes: Namespace) -> int:
    return abrir_como_usar()


def rodar_instalar(_opcoes: Namespace) -> int:
    return executar_comando_instalar()


def rodar_desinstalar(_opcoes: Namespace) -> int:
    return executar_comando_desinstalar()


def rodar_pentest(opcoes: Namespace) -> int:
    return executar_comando_pentest(opcoes.har, opcoes.saida, opcoes.autorizo)


def rodar_gravar(opcoes: Namespace) -> int:
    abrir_no_navegador = not opcoes.nao_abrir
    return gravar_e_analisar(
        opcoes.url, opcoes.saida, opcoes.ia, opcoes.sem_ia, abrir_no_navegador, opcoes.robo
    )


def rodar_analisar(opcoes: Namespace) -> int:
    abrir_no_navegador = not opcoes.nao_abrir
    if opcoes.sem_ia:
        return analisar_sem_ia(opcoes.har, opcoes.saida, abrir_no_navegador, opcoes.pentest)
    return analisar_com_ia(opcoes.har, opcoes.saida, opcoes.ia, abrir_no_navegador, opcoes.pentest)


COMANDO_PELO_NOME: dict[str, Callable[[Namespace], int]] = {
    "como-usar": rodar_como_usar,
    "instalar": rodar_instalar,
    "desinstalar": rodar_desinstalar,
    "pentest": rodar_pentest,
    "gravar": rodar_gravar,
    "analisar": rodar_analisar,
}
