import os
from pathlib import Path

from rastro.instalacao.path_no_unix import (
    FIM_DO_BLOCO,
    INICIO_DO_BLOCO,
    acrescentar_bloco_do_path,
    arquivo_do_shell,
    pasta_no_path,
    posicao_da_linha,
    remover_bloco_do_path,
)


def test_r17_3_pasta_no_path_reconhece_a_pasta_entre_as_outras(tmp_path: Path) -> None:
    pasta = tmp_path / ".local" / "bin"

    assert pasta_no_path(pasta, f"/usr/bin{os.pathsep}{pasta}")
    assert not pasta_no_path(pasta, "/usr/bin")


def test_r17_3_arquivo_do_shell_segue_o_shell_da_pessoa(tmp_path: Path) -> None:
    assert arquivo_do_shell(tmp_path, "/usr/bin/zsh") == tmp_path / ".zshrc"
    assert arquivo_do_shell(tmp_path, "/bin/bash") == tmp_path / ".bashrc"
    assert arquivo_do_shell(tmp_path, "/bin/fish") == tmp_path / ".profile"


def test_r17_3_bloco_do_path_vai_depois_do_texto_que_ja_existe(tmp_path: Path) -> None:
    arquivo = tmp_path / ".bashrc"
    arquivo.write_text("alias ll='ls -l'", encoding="utf-8")

    assert acrescentar_bloco_do_path(arquivo)

    texto = arquivo.read_text(encoding="utf-8")
    assert texto.startswith("alias ll='ls -l'\n\n")
    assert texto.endswith(f"{FIM_DO_BLOCO}\n")


def test_r17_3_remover_o_bloco_devolve_o_arquivo_como_era(tmp_path: Path) -> None:
    arquivo = tmp_path / ".bashrc"
    arquivo.write_text("alias ll='ls -l'\n", encoding="utf-8")
    acrescentar_bloco_do_path(arquivo)

    assert remover_bloco_do_path(arquivo)
    assert arquivo.read_text(encoding="utf-8") == "alias ll='ls -l'\n"


def test_r17_3_remover_o_bloco_de_arquivo_que_nao_existe_nao_faz_nada(tmp_path: Path) -> None:
    assert not remover_bloco_do_path(tmp_path / ".zshrc")
    assert not (tmp_path / ".zshrc").exists()


def test_r17_3_posicao_da_linha_ignora_espacos_e_comeca_onde_pedido() -> None:
    linhas = [f"  {INICIO_DO_BLOCO}\n", "x\n", f"{INICIO_DO_BLOCO}\n"]

    assert posicao_da_linha(linhas, INICIO_DO_BLOCO, 0) == 0
    assert posicao_da_linha(linhas, INICIO_DO_BLOCO, 1) == 2
    assert posicao_da_linha(linhas, FIM_DO_BLOCO, 0) is None
