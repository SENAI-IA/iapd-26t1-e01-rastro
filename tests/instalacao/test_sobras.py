from pathlib import Path

from rastro.instalacao.sobras import (
    DESCRICAO_DOS_ARQUIVOS,
    DESCRICAO_DOS_DADOS,
    Sobra,
    comando_para_apagar,
    sobras_da_instalacao,
)
from tests.instalacao.apoio import projeto_do_install_sh


def test_r17_4_sobras_trazem_a_pasta_criada_pelo_install_sh(tmp_path: Path) -> None:
    projeto = projeto_do_install_sh(tmp_path)

    assert sobras_da_instalacao(tmp_path, projeto) == [
        Sobra(DESCRICAO_DOS_ARQUIVOS, projeto)
    ]


def test_r17_4_sobras_nao_trazem_a_pasta_de_um_clone(tmp_path: Path) -> None:
    clone = tmp_path / "meu-clone"
    clone.mkdir()

    assert sobras_da_instalacao(tmp_path, clone) == []


def test_r17_4_sobras_trazem_as_gravacoes_e_relatorios(tmp_path: Path) -> None:
    dados = tmp_path / "Rastro"
    dados.mkdir()

    assert sobras_da_instalacao(tmp_path, tmp_path / "clone") == [
        Sobra(DESCRICAO_DOS_DADOS, dados)
    ]


def test_r17_4_comando_para_apagar_no_linux_protege_o_caminho() -> None:
    assert comando_para_apagar(Path("/home/ana/minha pasta"), no_windows=False) == (
        "rm -rf '/home/ana/minha pasta'"
    )


def test_r17_4_comando_para_apagar_no_windows_usa_o_powershell() -> None:
    assert comando_para_apagar(Path("C:/Users/d'ana/Rastro"), no_windows=True) == (
        "Remove-Item -Recurse -Force 'C:/Users/d''ana/Rastro'"
    )
