from typing import Any


def pacote_e_o_npm_procurado(pacote_da_fonte: Any, pacote: str) -> bool:
    return bool(pacote_da_fonte["ecosystem"] == "npm" and pacote_da_fonte["name"] == pacote)
