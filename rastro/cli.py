import sys

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
    if opcoes.comando == "como-usar":
        return abrir_como_usar()
    if opcoes.comando == "instalar":
        return executar_comando_instalar()
    if opcoes.comando == "desinstalar":
        return executar_comando_desinstalar()
    if opcoes.comando == "pentest":
        return executar_comando_pentest(opcoes.har, opcoes.saida, opcoes.autorizo)
    abrir_no_navegador = not opcoes.nao_abrir
    if opcoes.comando == "gravar":
        return gravar_e_analisar(
            opcoes.url, opcoes.saida, opcoes.ia, opcoes.sem_ia, abrir_no_navegador, opcoes.robo
        )
    if opcoes.sem_ia:
        return analisar_sem_ia(opcoes.har, opcoes.saida, abrir_no_navegador, opcoes.pentest)
    return analisar_com_ia(opcoes.har, opcoes.saida, opcoes.ia, abrir_no_navegador, opcoes.pentest)
