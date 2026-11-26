from typing import Any


def e_o_pacote_npm(pacote_da_fonte: Any, pacote: str) -> bool:
    return bool(pacote_da_fonte["ecosystem"] == "npm" and pacote_da_fonte["name"] == pacote)
