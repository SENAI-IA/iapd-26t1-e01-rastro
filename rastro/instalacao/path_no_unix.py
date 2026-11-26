import os
from pathlib import Path

INICIO_DO_BLOCO = "# >>> rastro >>> (criado por `rastro instalar`; `rastro desinstalar` remove)"
FIM_DO_BLOCO = "# <<< rastro <<<"
LINHA_DO_PATH = 'export PATH="$HOME/.local/bin:$PATH"'
ARQUIVOS_DO_SHELL = (".bashrc", ".zshrc", ".profile")
ARQUIVO_PELO_NOME_DO_SHELL = {"zsh": ".zshrc", "bash": ".bashrc"}
ARQUIVO_DE_QUALQUER_SHELL = ".profile"


def pasta_no_path(pasta: Path, path: str) -> bool:
    return any(parte_e_a_pasta(parte, pasta) for parte in path.split(os.pathsep))


def parte_e_a_pasta(parte: str, pasta: Path) -> bool:
    if not parte:
        return False
    return Path(parte) == pasta


def arquivo_do_shell(pasta_do_usuario: Path, shell: str) -> Path:
    nome = Path(shell).name
    return pasta_do_usuario / ARQUIVO_PELO_NOME_DO_SHELL.get(nome, ARQUIVO_DE_QUALQUER_SHELL)


def acrescentar_bloco_do_path(arquivo: Path) -> bool:
    texto = texto_do_arquivo_se_existir(arquivo)
    if INICIO_DO_BLOCO in texto:
        return False
    quebra_que_falta = quebra_de_linha_que_falta_no_fim(texto)
    bloco = f"{quebra_que_falta}\n{INICIO_DO_BLOCO}\n{LINHA_DO_PATH}\n{FIM_DO_BLOCO}\n"
    with arquivo.open("a", encoding="utf-8") as arquivo_aberto:
        arquivo_aberto.write(bloco)
    return True


def texto_do_arquivo_se_existir(arquivo: Path) -> str:
    if not arquivo.is_file():
        return ""
    return arquivo.read_text(encoding="utf-8")


def quebra_de_linha_que_falta_no_fim(texto: str) -> str:
    if texto == "" or texto.endswith("\n"):
        return ""
    return "\n"


def remover_bloco_do_path(arquivo: Path) -> bool:
    if not arquivo.is_file():
        return False
    linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)
    inicio = posicao_da_linha(linhas, INICIO_DO_BLOCO, 0)
    if inicio is None:
        return False
    fim = posicao_da_linha(linhas, FIM_DO_BLOCO, inicio)
    if fim is None:
        return False
    if linha_em_branco_antes(linhas, inicio):
        inicio -= 1
    linhas_que_ficam = linhas[:inicio] + linhas[fim + 1 :]
    arquivo.write_text("".join(linhas_que_ficam), encoding="utf-8")
    return True


def linha_em_branco_antes(linhas: list[str], posicao: int) -> bool:
    return posicao > 0 and linhas[posicao - 1].strip() == ""


def posicao_da_linha(linhas: list[str], procurada: str, a_partir_de: int) -> int | None:
    for posicao in range(a_partir_de, len(linhas)):
        if linhas[posicao].strip() == procurada:
            return posicao
    return None
