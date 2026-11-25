import os
import subprocess
import sys
from pathlib import Path

import pytest

from rastro import atalho
from rastro.atalho import (
    INICIO_DO_BLOCO,
    MARCA,
    MARCA_DO_INSTALADOR,
    AtalhoDeOutro,
    Sobra,
    comando_para_apagar,
    desinstalar_no_unix,
    instalar_no_unix,
    sobras_da_instalacao,
    texto_do_atalho_windows,
)

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
PATH_SEM_A_PASTA = "/usr/bin:/bin"
somente_unix = pytest.mark.skipif(os.name == "nt", reason="atalho de shell do Linux")


def atalho_unix(casa: Path) -> Path:
    return casa / ".local" / "bin" / "rastro"


def ambiente(casa: Path, path: str = PATH_SEM_A_PASTA, shell: str = "/bin/bash") -> dict[str, str]:
    return {"PATH": path, "SHELL": shell, "HOME": str(casa)}


def test_r17_3_instalar_cria_o_atalho_marcado_na_pasta_do_usuario(tmp_path: Path) -> None:
    instalacao = instalar_no_unix(tmp_path, ambiente(tmp_path))

    assert instalacao.atalho == atalho_unix(tmp_path)
    assert instalacao.projeto == RAIZ_DO_PROJETO
    texto = instalacao.atalho.read_text(encoding="utf-8")
    assert MARCA in texto
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


def test_r17_3_atalho_do_windows_chama_o_rastro_do_projeto() -> None:
    texto = texto_do_atalho_windows(Path("C:/Python310/python.exe"), Path("C:/rastro"))

    assert MARCA in texto
    assert "PYTHONPATH=" in texto
    assert "-m rastro %* & exit /b" in texto
    assert texto.endswith("\r\n")


def test_r17_3_python_do_atalho_fica_fora_do_venv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "prefix", "/projeto/.venv")
    monkeypatch.setattr(sys, "base_prefix", sys.base_prefix)

    python = atalho.python_do_sistema()

    assert ".venv" not in python.parts


def projeto_do_install_sh(casa: Path) -> Path:
    projeto = casa / ".local" / "share" / "rastro"
    projeto.mkdir(parents=True)
    (projeto / MARCA_DO_INSTALADOR).touch()
    return projeto


def test_r17_4_sobras_trazem_a_pasta_criada_pelo_install_sh(tmp_path: Path) -> None:
    projeto = projeto_do_install_sh(tmp_path)

    assert sobras_da_instalacao(tmp_path, projeto) == [
        Sobra(atalho.DESCRICAO_DOS_ARQUIVOS, projeto)
    ]


def test_r17_4_sobras_nao_trazem_a_pasta_de_um_clone(tmp_path: Path) -> None:
    clone = tmp_path / "meu-clone"
    clone.mkdir()

    assert sobras_da_instalacao(tmp_path, clone) == []


def test_r17_4_sobras_trazem_as_gravacoes_e_relatorios(tmp_path: Path) -> None:
    dados = tmp_path / "Rastro"
    dados.mkdir()

    assert sobras_da_instalacao(tmp_path, tmp_path / "clone") == [
        Sobra(atalho.DESCRICAO_DOS_DADOS, dados)
    ]


def test_r17_4_comando_para_apagar_no_linux_protege_o_caminho() -> None:
    assert comando_para_apagar(Path("/home/ana/minha pasta"), no_windows=False) == (
        "rm -rf '/home/ana/minha pasta'"
    )


def test_r17_4_comando_para_apagar_no_windows_usa_o_powershell() -> None:
    assert comando_para_apagar(Path("C:/Users/d'ana/Rastro"), no_windows=True) == (
        "Remove-Item -Recurse -Force 'C:/Users/d''ana/Rastro'"
    )
