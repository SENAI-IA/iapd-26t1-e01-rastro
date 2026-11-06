import argparse

DESCRICAO = (
    "Lê um HAR, identifica as bibliotecas front-end do site e prioriza as falhas "
    "conhecidas nelas. Só análise passiva: o site analisado nunca é acessado."
)


def criar_leitor_de_argumentos() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(prog="rastro", description=DESCRICAO)


def executar(argumentos: list[str] | None = None) -> int:
    leitor = criar_leitor_de_argumentos()
    leitor.parse_args(argumentos)
    leitor.print_help()
    return 0
