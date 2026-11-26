import os
import subprocess
from pathlib import Path

import pytest

from rastro.instalacao.atalho import MARCA_DO_ATALHO, AtalhoDeOutro
from rastro.instalacao.instalador import desinstalar_no_unix, instalar_no_unix
from rastro.instalacao.path_no_unix import INICIO_DO_BLOCO
from tests.instalacao.apoio import PATH_SEM_A_PASTA, ambiente, atalho_unix, somente_unix

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent.parent


def test_r17_3_instalar_cria_o_atalho_marcado_na_pasta_do_usuario(tmp_path: Path) -> None:
    instalacao = instalar_no_unix(tmp_path, ambiente(tmp_path))

    assert instalacao.atalho == atalho_unix(tmp_path)
    assert instalacao.projeto == RAIZ_DO_PROJETO
    texto = instalacao.atalho.read_text(encoding="utf-8")
    assert MARCA_DO_ATALHO in texto
    assert str(RAIZ_DO_PROJETO) in texto
    assert os.access(instalacao.atalho, os.X_OK)


@somente_unix
def test_r18_1_atalho_roda_o_rastro_de_outra_pasta(tmp_path: Path) -> None:
    instalacao = instalar_no_unix(tmp_path, ambiente(tmp_path))
    outra_pasta = tmp_path / "Downloads"
    outra_pasta.mkdir()

    resultado = subprocess.run(
        [str(instalacao.atalho), "--help"],
        cwd=outra_pasta,
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert "usage: rastro" in resultado.stdout


def test_r17_3_instalar_poe_a_pasta_no_path_do_shell_da_pessoa(tmp_path: Path) -> None:
    instalacao = instalar_no_unix(tmp_path, ambiente(tmp_path, shell="/usr/bin/zsh"))

    zshrc = tmp_path / ".zshrc"
    assert instalacao.path_alterado_em == str(zshrc)
    texto = zshrc.read_text(encoding="utf-8")
    assert INICIO_DO_BLOCO in texto
    assert "$HOME/.local/bin" in texto


def test_r17_3_instalar_nao_mexe_no_shell_se_a_pasta_ja_esta_no_path(tmp_path: Path) -> None:
    path = f"{tmp_path / '.local' / 'bin'}{os.pathsep}{PATH_SEM_A_PASTA}"

    instalacao = instalar_no_unix(tmp_path, ambiente(tmp_path, path=path))

    assert instalacao.path_alterado_em is None
    assert not (tmp_path / ".bashrc").exists()


def test_r17_3_instalar_de_novo_nao_repete_o_bloco_do_path(tmp_path: Path) -> None:
    instalar_no_unix(tmp_path, ambiente(tmp_path))
    segunda = instalar_no_unix(tmp_path, ambiente(tmp_path))

    assert segunda.path_alterado_em is None
    assert (tmp_path / ".bashrc").read_text(encoding="utf-8").count(INICIO_DO_BLOCO) == 1


def test_r17_3_instalar_nao_sobrescreve_comando_rastro_de_outro(tmp_path: Path) -> None:
    outro = atalho_unix(tmp_path)
    outro.parent.mkdir(parents=True)
    outro.write_text("#!/bin/sh\necho pipx\n", encoding="utf-8")

    with pytest.raises(AtalhoDeOutro, match="pipx"):
        instalar_no_unix(tmp_path, ambiente(tmp_path))

    assert outro.read_text(encoding="utf-8") == "#!/bin/sh\necho pipx\n"
    assert not (tmp_path / ".bashrc").exists()


def test_r17_3_desinstalar_remove_so_o_que_o_instalar_criou(tmp_path: Path) -> None:
    bashrc = tmp_path / ".bashrc"
    bashrc.write_text("alias ll='ls -l'\n", encoding="utf-8")
    instalar_no_unix(tmp_path, ambiente(tmp_path))

    desinstalacao = desinstalar_no_unix(tmp_path)

    assert desinstalacao.atalho_removido == atalho_unix(tmp_path)
    assert desinstalacao.path_removido_de == [str(bashrc)]
    assert not atalho_unix(tmp_path).exists()
    assert bashrc.read_text(encoding="utf-8") == "alias ll='ls -l'\n"


def test_r17_3_desinstalar_sem_nada_instalado_nao_altera_nada(tmp_path: Path) -> None:
    desinstalacao = desinstalar_no_unix(tmp_path)

    assert desinstalacao.atalho_removido is None
    assert desinstalacao.path_removido_de == []
    assert list(tmp_path.iterdir()) == []


def test_r17_3_desinstalar_nao_apaga_comando_rastro_de_outro(tmp_path: Path) -> None:
    outro = atalho_unix(tmp_path)
    outro.parent.mkdir(parents=True)
    outro.write_text("#!/bin/sh\necho pipx\n", encoding="utf-8")

    with pytest.raises(AtalhoDeOutro):
        desinstalar_no_unix(tmp_path)

    assert outro.exists()


def test_r17_3_desinstalar_deixa_bloco_sem_fim_como_esta(tmp_path: Path) -> None:
    bashrc = tmp_path / ".bashrc"
    texto = f"{INICIO_DO_BLOCO}\nexport PATH=/x:$PATH\n"
    bashrc.write_text(texto, encoding="utf-8")

    assert desinstalar_no_unix(tmp_path).path_removido_de == []
    assert bashrc.read_text(encoding="utf-8") == texto
