import shutil

IA_PADRAO = "kiro"
VARIAVEL_DA_IA = "RASTRO_IA"
EXECUTAVEIS_DAS_IAS: dict[str, str] = {
    "kiro": "kiro-cli",
    "claude": "claude",
    "codex": "codex",
}


class ErroNaEscolhaDaIA(Exception):
    pass


class IAInvalida(ErroNaEscolhaDaIA):
    def __init__(self, nome: str, origem: str) -> None:
        opcoes = ", ".join(EXECUTAVEIS_DAS_IAS)
        super().__init__(f"IA inválida em {origem}: '{nome}'. Opções válidas: {opcoes}.")


class CLIDaIAAusente(ErroNaEscolhaDaIA):
    def __init__(self, nome: str, executavel: str) -> None:
        super().__init__(f"a CLI da IA {nome} ({executavel}) não foi encontrada no sistema")


def escolher_ia(opcao_da_ia: str | None, variavel_de_ambiente: str | None) -> str:
    if opcao_da_ia is not None:
        return validar_ia(opcao_da_ia, "--ia")
    if variavel_de_ambiente:
        return validar_ia(variavel_de_ambiente, VARIAVEL_DA_IA)
    return IA_PADRAO


def validar_ia(nome: str, origem: str) -> str:
    normalizado = nome.strip().lower()
    if normalizado not in EXECUTAVEIS_DAS_IAS:
        raise IAInvalida(nome, origem)
    return normalizado


def localizar_cli(nome_da_ia: str) -> str:
    executavel = EXECUTAVEIS_DAS_IAS[nome_da_ia]
    caminho = shutil.which(executavel)
    if caminho is None:
        raise CLIDaIAAusente(nome_da_ia, executavel)
    return caminho
