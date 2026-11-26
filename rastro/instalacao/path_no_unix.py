import os
from pathlib import Path

INICIO_DO_BLOCO = "# >>> rastro >>> (criado por `rastro instalar`; `rastro desinstalar` remove)"
FIM_DO_BLOCO = "# <<< rastro <<<"
LINHA_DO_PATH = 'export PATH="$HOME/.local/bin:$PATH"'
ARQUIVOS_DO_SHELL = (".bashrc", ".zshrc", ".profile")


def pasta_no_path(pasta: Path, path: str) -> bool:
    return any(Path(parte) == pasta for parte in path.split(os.pathsep) if parte)


def arquivo_do_shell(pasta_do_usuario: Path, shell: str) -> Path:
    nome = Path(shell).name
    if nome == "zsh":
        return pasta_do_usuario / ".zshrc"
    if nome == "bash":
        return pasta_do_usuario / ".bashrc"
    return pasta_do_usuario / ".profile"


def acrescentar_bloco_do_path(arquivo: Path) -> bool:
    texto = arquivo.read_text(encoding="utf-8") if arquivo.is_file() else ""
    if INICIO_DO_BLOCO in texto:
        return False
    quebra_que_falta = "" if texto == "" or texto.endswith("\n") else "\n"
    bloco = f"{quebra_que_falta}\n{INICIO_DO_BLOCO}\n{LINHA_DO_PATH}\n{FIM_DO_BLOCO}\n"
    with arquivo.open("a", encoding="utf-8") as saida:
        saida.write(bloco)
    return True


def remover_bloco_do_path(arquivo: Path) -> bool:
    if not arquivo.is_file():
        return False
    linhas = arquivo.read_text(encoding="utf-8").splitlines(keepends=True)
    inicio = posicao_da_linha(linhas, INICIO_DO_BLOCO, 0)
    fim = posicao_da_linha(linhas, FIM_DO_BLOCO, inicio) if inicio is not None else None
    if inicio is None or fim is None:
        return False
    if inicio > 0 and linhas[inicio - 1].strip() == "":
        inicio -= 1
    arquivo.write_text("".join(linhas[:inicio] + linhas[fim + 1 :]), encoding="utf-8")
    return True


def posicao_da_linha(linhas: list[str], procurada: str, a_partir_de: int) -> int | None:
    posicoes = range(a_partir_de, len(linhas))
    return next((i for i in posicoes if linhas[i].strip() == procurada), None)
