import sys

from rastro.comandos.argumentos import criar_leitor_de_argumentos
from rastro.comandos.comando_analisar import analisar_com_ia, analisar_sem_ia
from rastro.comandos.comando_como_usar import abrir_como_usar
from rastro.comandos.comando_desinstalar import desinstalar_comando
from rastro.comandos.comando_gravar import gravar_e_analisar
from rastro.comandos.comando_instalar import instalar_comando
from rastro.comandos.comando_pentest import pentest_comando


def principal() -> None:
    sys.exit(executar())


def executar(argumentos: list[str] | None = None) -> int:
    leitor = criar_leitor_de_argumentos()
    opcoes = leitor.parse_args(argumentos)
    if opcoes.comando is None:
        leitor.print_help()
        return 0
    if opcoes.comando == "como-usar":
        return abrir_como_usar()
    if opcoes.comando == "instalar":
        return instalar_comando()
    if opcoes.comando == "desinstalar":
        return desinstalar_comando()
    if opcoes.comando == "pentest":
        return pentest_comando(opcoes.har, opcoes.saida, opcoes.autorizo)
    abrir = not opcoes.nao_abrir
    if opcoes.comando == "gravar":
        return gravar_e_analisar(
            opcoes.url, opcoes.saida, opcoes.ia, opcoes.sem_ia, abrir, opcoes.robo
        )
    if opcoes.sem_ia:
        return analisar_sem_ia(opcoes.har, opcoes.saida, abrir, opcoes.pentest)
    return analisar_com_ia(opcoes.har, opcoes.saida, opcoes.ia, abrir, opcoes.pentest)
