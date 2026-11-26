COR_DE_DESTAQUE_ANSI = "\x1b[1;33m"
FIM_DO_DESTAQUE = "\x1b[0m"
SEGUNDOS_POR_MINUTO = 60


def destacar(texto: str) -> str:
    linhas = [destacar_linha(linha) for linha in texto.split("\n")]
    return "\n".join(linhas)


def destacar_linha(linha: str) -> str:
    return COR_DE_DESTAQUE_ANSI + linha + FIM_DO_DESTAQUE


def escrever_tempo(segundos: float) -> str:
    segundos_inteiros = int(segundos)
    minutos = segundos_inteiros // SEGUNDOS_POR_MINUTO
    segundos_do_minuto = segundos_inteiros % SEGUNDOS_POR_MINUTO
    return f"{minutos}:{segundos_do_minuto:02d}"


def cortar_no_limite(texto: str, largura: int) -> str:
    if len(texto) <= largura:
        return texto
    return texto[: max(largura - 1, 0)] + "…"
