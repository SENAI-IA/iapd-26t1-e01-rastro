import shutil
import subprocess
import sys
import zipfile
from importlib import metadata
from pathlib import Path

import pytest

RAIZ_DO_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DOS_PROMPTS = RAIZ_DO_PROJETO / "rastro" / "ia" / "prompts"
SETUPTOOLS_MINIMO = (70, 1)
TEXTO_SETUPTOOLS_ANTIGO = (
    "Este teste monta o pacote sem rede e precisa do setuptools {minimo} ou mais novo "
    "no .venv (encontrado: {encontrado}). Com o .venv ativo, rode: "
    "pip install -r requirements-dev.txt"
)


def versao_do_setuptools() -> str | None:
    try:
        return metadata.version("setuptools")
    except metadata.PackageNotFoundError:
        return None


def setuptools_serve(versao: str | None) -> bool:
    if versao is None:
        return False
    maior, menor = versao.split(".")[:2]
    return (int(maior), int(menor)) >= SETUPTOOLS_MINIMO


def exigir_setuptools_novo() -> None:
    versao = versao_do_setuptools()
    if not setuptools_serve(versao):
        minimo = ".".join(str(parte) for parte in SETUPTOOLS_MINIMO)
        pytest.fail(
            TEXTO_SETUPTOOLS_ANTIGO.format(minimo=minimo, encontrado=versao or "nenhum"),
            pytrace=False,
        )


@pytest.fixture(scope="module")
def pacote_montado(tmp_path_factory: pytest.TempPathFactory) -> zipfile.ZipFile:
    exigir_setuptools_novo()
    copia = tmp_path_factory.mktemp("projeto")
    shutil.copy(RAIZ_DO_PROJETO / "pyproject.toml", copia)
    shutil.copytree(
        RAIZ_DO_PROJETO / "rastro",
        copia / "rastro",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            ".",
            "--no-deps",
            "--no-build-isolation",
            "--no-index",
            "--disable-pip-version-check",
            "--quiet",
            "--wheel-dir",
            "pacote",
        ],
        cwd=copia,
        capture_output=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr
    return zipfile.ZipFile(next((copia / "pacote").glob("rastro-*.whl")))


def ler_do_pacote(pacote: zipfile.ZipFile, terminacao: str) -> str:
    nome = next(nome for nome in pacote.namelist() if nome.endswith(terminacao))
    return pacote.read(nome).decode("utf-8")


def test_r18_1_pacote_cria_o_comando_rastro(pacote_montado: zipfile.ZipFile) -> None:
    pontos_de_entrada = ler_do_pacote(pacote_montado, ".dist-info/entry_points.txt")

    assert "[console_scripts]" in pontos_de_entrada
    assert "rastro = rastro.cli:principal" in pontos_de_entrada


def test_r18_1_pacote_leva_o_modelo_do_relatorio(pacote_montado: zipfile.ZipFile) -> None:
    assert "rastro/relatorio/modelo.html" in pacote_montado.namelist()


def test_r18_1_pacote_leva_todos_os_prompts(pacote_montado: zipfile.ZipFile) -> None:
    prompts = sorted(PASTA_DOS_PROMPTS.glob("*.md"))

    assert prompts
    for prompt in prompts:
        assert f"rastro/ia/prompts/{prompt.name}" in pacote_montado.namelist()
