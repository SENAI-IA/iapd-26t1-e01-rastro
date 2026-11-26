import re


def versao_esta_no_trecho(versao: str, trecho: str) -> bool:
    return padrao_da_versao_isolada(versao).search(trecho) is not None


def padrao_da_versao_isolada(versao: str) -> re.Pattern[str]:
    sem_numero_antes = r"(?<!\d)(?<!\d\.)"
    sem_continuacao_depois = r"(?!\d|\.\d|-[0-9A-Za-z])"
    return re.compile(sem_numero_antes + re.escape(versao) + sem_continuacao_depois)
