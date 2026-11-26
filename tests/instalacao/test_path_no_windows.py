import sys
from pathlib import Path

import pytest

from rastro.instalacao.path_no_windows import (
    acrescentar_pasta,
    avisar_terminais_novos_do_windows,
    mesma_pasta_no_windows,
    pasta_do_windows,
    tirar_pasta,
    trocar_path_do_windows,
)

PASTA = Path("C:/Users/ana/AppData/Local/Rastro/bin")
somente_fora_do_windows = pytest.mark.skipif(
    sys.platform == "win32", reason="o registro do Windows existe de verdade"
)


def test_r17_3_pasta_do_windows_usa_o_localappdata(tmp_path: Path) -> None:
    local = tmp_path / "Local"

    assert pasta_do_windows(tmp_path, {"LOCALAPPDATA": str(local)}) == local / "Rastro" / "bin"


def test_r17_3_pasta_do_windows_sem_localappdata_fica_na_pasta_do_usuario(
    tmp_path: Path,
) -> None:
    esperada = tmp_path / "AppData" / "Local" / "Rastro" / "bin"

    assert pasta_do_windows(tmp_path, {}) == esperada


def test_r17_3_mesma_pasta_no_windows_ignora_maiusculas() -> None:
    assert mesma_pasta_no_windows(str(PASTA).upper(), PASTA)
    assert not mesma_pasta_no_windows("C:/Windows", PASTA)


def test_r17_3_acrescentar_pasta_ao_path_nao_repete() -> None:
    assert acrescentar_pasta(["C:/Windows"], PASTA) == ["C:/Windows", str(PASTA)]
    assert acrescentar_pasta([str(PASTA).lower()], PASTA) == [str(PASTA).lower()]


def test_r17_3_tirar_pasta_do_path_deixa_as_outras() -> None:
    assert tirar_pasta(["C:/Windows", str(PASTA)], PASTA) == ["C:/Windows"]


@somente_fora_do_windows
def test_r17_3_path_do_registro_so_e_trocado_no_windows() -> None:
    with pytest.raises(OSError, match="só existe no Windows"):
        trocar_path_do_windows(lambda partes: partes)


@somente_fora_do_windows
def test_r17_3_aviso_aos_terminais_fora_do_windows_nao_faz_nada() -> None:
    avisar_terminais_novos_do_windows()
