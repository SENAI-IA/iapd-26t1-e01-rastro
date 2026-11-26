from importlib import resources

MARCADOR_DA_ENTRADA = "{{entrada}}"


def montar_prompt(nome_do_arquivo: str, entrada: str) -> str:
    return ler_modelo_do_prompt(nome_do_arquivo).replace(MARCADOR_DA_ENTRADA, entrada)


def ler_modelo_do_prompt(nome_do_arquivo: str) -> str:
    prompts = resources.files("rastro.ia").joinpath("prompts")
    return prompts.joinpath(nome_do_arquivo).read_text(encoding="utf-8")
