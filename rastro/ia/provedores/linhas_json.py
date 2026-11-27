import json
from typing import Any


def ler_eventos(saida_da_cli: str) -> list[dict[str, Any]]:
    eventos = []
    for linha in saida_da_cli.splitlines():
        evento = ler_linha(linha)
        if evento is not None:
            eventos.append(evento)
    return eventos


def ler_linha(linha: str) -> dict[str, Any] | None:
    try:
        evento = json.loads(linha)
    except json.JSONDecodeError:
        return None
    if not isinstance(evento, dict):
        return None
    return evento
