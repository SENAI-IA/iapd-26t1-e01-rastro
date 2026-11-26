COR_DE_DESTAQUE_ANSI = "\x1b[1;33m"
FIM_DO_DESTAQUE = "\x1b[0m"


def destacar(texto: str) -> str:
    return "\n".join(
        f"{COR_DE_DESTAQUE_ANSI}{linha}{FIM_DO_DESTAQUE}" for linha in texto.split("\n")
    )


def escrever_tempo(segundos: float) -> str:
    minutos, resto = divmod(int(segundos), 60)
    return f"{minutos}:{resto:02d}"


def cortar_no_limite(texto: str, largura: int) -> str:
    if len(texto) <= largura:
        return texto
    return texto[: max(largura - 1, 0)] + "…"
