import io


def ultima_tela(saida: io.StringIO) -> str:
    return saida.getvalue().split("\r")[-1].rstrip()
