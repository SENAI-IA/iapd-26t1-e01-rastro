from datetime import datetime

LETRA_DO_UTC = "Z"
DESLOCAMENTO_DO_UTC = "+00:00"


def ler_data_iso(texto: str) -> datetime:
    com_deslocamento = texto.replace(LETRA_DO_UTC, DESLOCAMENTO_DO_UTC)
    return datetime.fromisoformat(com_deslocamento)
