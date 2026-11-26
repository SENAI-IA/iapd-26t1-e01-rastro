import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from rastro.instalacao.atalho import MARCA_DO_ATALHO
from rastro.instalacao.sobras import MARCA_DO_INSTALADOR

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
INSTALADOR = RAIZ_DO_PROJETO / "install.sh"

pytestmark = pytest.mark.skipif(
    os.name == "nt" or shutil.which("sh") is None or shutil.which("curl") is None,
    reason="o install.sh é do Linux e precisa do sh e do curl",
)


@pytest.fixture
def pacote_igual_ao_do_github(tmp_path: Path) -> Path:
    caminho = tmp_path / "rastro-main.tar.gz"
    sem_cache = shutil.ignore_patterns("__pycache__")
    copia = tmp_path / "montagem" / "iapd-26t1-e01-rastro-main"
    shutil.copytree(RAIZ_DO_PROJETO / "rastro", copia / "rastro", ignore=sem_cache)
    shutil.copy(RAIZ_DO_PROJETO / "pyproject.toml", copia)
    with tarfile.open(caminho, "w:gz") as arquivo:
        arquivo.add(copia, arcname=copia.name)
    return caminho


def rodar_instalador(pasta_do_usuario: Path, origem: str) -> subprocess.CompletedProcess[str]:
    pasta_do_python = str(Path(sys.executable).parent)
    ambiente = {
        "HOME": str(pasta_do_usuario),
        "SHELL": "/bin/bash",
        "PATH": f"{pasta_do_python}{os.pathsep}/usr/bin{os.pathsep}/bin",
        "RASTRO_ORIGEM": origem,
    }
    return subprocess.run(
        ["sh", str(INSTALADOR)],
        env=ambiente,
        cwd=pasta_do_usuario,
        capture_output=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )


def pasta_instalada(pasta_do_usuario: Path) -> Path:
    return pasta_do_usuario / ".local" / "share" / "rastro"


def test_r17_4_instalador_baixa_o_rastro_e_cria_o_comando(
    tmp_path: Path, pacote_igual_ao_do_github: Path
) -> None:
    resultado = rodar_instalador(tmp_path, pacote_igual_ao_do_github.as_uri())

    assert resultado.returncode == 0, resultado.stderr
    pasta = pasta_instalada(tmp_path)
    assert (pasta / "rastro" / "__main__.py").is_file()
    assert (pasta / MARCA_DO_INSTALADOR).is_file()
    comando = tmp_path / ".local" / "bin" / "rastro"
    assert MARCA_DO_ATALHO in comando.read_text(encoding="utf-8")
    assert str(pasta) in comando.read_text(encoding="utf-8")
    assert "Pronto! Comando rastro instalado." in resultado.stdout


def test_r17_4_comando_instalado_funciona(tmp_path: Path, pacote_igual_ao_do_github: Path) -> None:
    rodar_instalador(tmp_path, pacote_igual_ao_do_github.as_uri())

    ajuda = subprocess.run(
        [str(tmp_path / ".local" / "bin" / "rastro"), "--help"],
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )

    assert ajuda.returncode == 0, ajuda.stderr
    assert "usage: rastro" in ajuda.stdout


def test_r17_4_rodar_de_novo_atualiza_sem_sobras(
    tmp_path: Path, pacote_igual_ao_do_github: Path
) -> None:
    rodar_instalador(tmp_path, pacote_igual_ao_do_github.as_uri())
    velho = pasta_instalada(tmp_path) / "arquivo-da-versao-velha.txt"
    velho.write_text("velho", encoding="utf-8")

    resultado = rodar_instalador(tmp_path, pacote_igual_ao_do_github.as_uri())

    assert resultado.returncode == 0, resultado.stderr
    assert not velho.exists()
    irmas = sorted(pasta.name for pasta in pasta_instalada(tmp_path).parent.iterdir())
    assert irmas == ["rastro"]


def test_r17_4_nao_mexe_numa_pasta_que_nao_criou(
    tmp_path: Path, pacote_igual_ao_do_github: Path
) -> None:
    alheia = pasta_instalada(tmp_path)
    alheia.mkdir(parents=True)
    (alheia / "meu.txt").write_text("meu", encoding="utf-8")

    resultado = rodar_instalador(tmp_path, pacote_igual_ao_do_github.as_uri())

    assert resultado.returncode == 1
    assert "não foi criada por este instalador" in resultado.stderr
    assert sorted(item.name for item in alheia.iterdir()) == ["meu.txt"]


def test_r17_4_falha_no_download_nao_deixa_nada(tmp_path: Path) -> None:
    sumido = (tmp_path / "nao-existe.tar.gz").as_uri()

    resultado = rodar_instalador(tmp_path, sumido)

    assert resultado.returncode == 1
    assert "não foi possível baixar o Rastro" in resultado.stderr
    assert list(pasta_instalada(tmp_path).parent.iterdir()) == []
