from collections.abc import Hashable, Iterable
from typing import TypeVar

Item = TypeVar("Item", bound=Hashable)


def sem_repeticao(itens: Iterable[Item]) -> list[Item]:
    ja_vistos: set[Item] = set()
    unicos: list[Item] = []
    for item in itens:
        if item not in ja_vistos:
            ja_vistos.add(item)
            unicos.append(item)
    return unicos
