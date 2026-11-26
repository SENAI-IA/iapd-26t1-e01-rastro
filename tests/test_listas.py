from rastro.listas import sem_repeticao


def test_sem_repeticao_tira_os_repetidos_e_mantem_a_ordem_da_primeira_vez() -> None:
    assert sem_repeticao(["GHSA-b", "GHSA-a", "GHSA-b", "GHSA-c", "GHSA-a"]) == [
        "GHSA-b",
        "GHSA-a",
        "GHSA-c",
    ]


def test_sem_repeticao_aceita_um_gerador() -> None:
    fontes = (fonte for fonte in ["OSV", "NVD", "OSV"])

    assert sem_repeticao(fontes) == ["OSV", "NVD"]


def test_sem_repeticao_de_lista_vazia_devolve_lista_vazia() -> None:
    assert sem_repeticao([]) == []
