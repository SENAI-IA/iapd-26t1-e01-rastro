from typing import Any, TypeGuard


def somar_tokens(uso: Any, campos_de_tokens: tuple[str, ...]) -> int | None:
    if not isinstance(uso, dict):
        return None
    total = 0
    for campo in campos_de_tokens:
        contagem = uso.get(campo)
        if not contagem_de_tokens_valida(contagem):
            return None
        total += contagem
    return total


def contagem_de_tokens_valida(contagem: Any) -> TypeGuard[int]:
    return isinstance(contagem, int) and not isinstance(contagem, bool) and contagem >= 0
