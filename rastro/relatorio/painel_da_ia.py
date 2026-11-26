from dataclasses import asdict
from typing import Any

from rastro.ia.cliente import ChamadaDaIA
from rastro.modelos_da_analise import Analise


def montar_painel_da_ia(analise: Analise) -> dict[str, Any]:
    return {
        "chamadas": [asdict(chamada) for chamada in analise.chamadas_de_ia],
        "travas_acionadas": [asdict(trava) for trava in analise.travas_acionadas],
        "com_e_sem_ia": comparar_com_e_sem_ia(analise),
        "tokens_total": tokens_total(analise),
    }


def comparar_com_e_sem_ia(analise: Analise) -> dict[str, dict[str, int]] | None:
    if analise.provedor_de_ia is None:
        return None
    achados_por_assinatura = [
        achado for achado in analise.achados if achado.biblioteca.metodo == "assinatura"
    ]
    bibliotecas_por_assinatura = [
        biblioteca for biblioteca in analise.bibliotecas if biblioteca.metodo == "assinatura"
    ]
    return {
        "bibliotecas": contagem_com_e_sem_ia(
            len(bibliotecas_por_assinatura), len(analise.bibliotecas)
        ),
        "achados": contagem_com_e_sem_ia(len(achados_por_assinatura), len(analise.achados)),
    }


def contagem_com_e_sem_ia(so_por_assinatura: int, com_ia: int) -> dict[str, int]:
    return {"so_por_assinatura": so_por_assinatura, "com_ia": com_ia}


def tokens_total(analise: Analise) -> int | None:
    if analise.provedor_de_ia is None:
        return None
    return somar_tokens(analise.chamadas_de_ia)


def somar_tokens(chamadas: list[ChamadaDaIA]) -> int | None:
    total = 0
    for chamada in chamadas:
        if chamada.tokens is None:
            return None
        total += chamada.tokens
    return total
