import json
from datetime import datetime
from pathlib import Path

import pytest

from rastro.relatorio.gravacao import (
    RelatorioJaExiste,
    caminho_do_relatorio,
    gravar_relatorio,
    nome_da_aplicacao,
    nome_de_pasta_seguro,
    pasta_padrao,
)

MOMENTO = datetime(2026, 11, 20, 14, 3, 0)
CARACTERES_PROIBIDOS_NO_WINDOWS = '<>:"/\\|?*'


def test_r13_1_pasta_da_analise_por_aplicacao_e_data_e_hora(tmp_path: Path) -> None:
    pasta = caminho_do_relatorio(tmp_path, "loja.exemplo.com", MOMENTO)

    assert pasta == tmp_path / "loja.exemplo.com" / "2026-11-20_14-03-00"


def test_r13_1_grava_o_json_numa_pasta_nova(tmp_path: Path) -> None:
    pasta = caminho_do_relatorio(tmp_path / "relatorios", "loja.exemplo.com", MOMENTO)

    caminho = gravar_relatorio(pasta, {"versao_formato": 1, "site": "loja.exemplo.com"})

    assert caminho == pasta / "relatorio.json"
    with caminho.open(encoding="utf-8") as arquivo:
        assert json.load(arquivo) == {"versao_formato": 1, "site": "loja.exemplo.com"}


def test_r13_1_json_em_utf_8_legivel(tmp_path: Path) -> None:
    caminho = gravar_relatorio(tmp_path / "analise", {"texto": "não procurado"})

    assert "não procurado" in caminho.read_text(encoding="utf-8")


def test_r13_2_pasta_padrao_fica_na_pasta_do_usuario(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert pasta_padrao() == tmp_path / "Rastro" / "relatorios"


def test_r13_3_sem_site_usa_o_nome_do_har() -> None:
    assert nome_da_aplicacao(None, Path("capturas") / "intranet.har") == "intranet"


def test_r13_3_com_site_usa_o_site() -> None:
    assert nome_da_aplicacao("loja.exemplo.com", Path("loja.har")) == "loja.exemplo.com"


def test_r13_3_porta_vira_sublinhado() -> None:
    assert nome_de_pasta_seguro("localhost:3000") == "localhost_3000"


@pytest.mark.parametrize("caractere", list(CARACTERES_PROIBIDOS_NO_WINDOWS))
def test_r13_3_caractere_proibido_no_windows_vira_sublinhado(caractere: str) -> None:
    assert nome_de_pasta_seguro(f"site{caractere}x") == "site_x"


def test_r13_3_ponto_e_espaco_no_fim_saem() -> None:
    assert nome_de_pasta_seguro("site. ") == "site"


def test_r13_3_nome_vazio_ou_so_pontos_nao_sobe_de_pasta() -> None:
    assert nome_de_pasta_seguro("") == "_"
    assert nome_de_pasta_seguro("..") == "_"


@pytest.mark.parametrize("reservado", ["CON", "nul", "COM1", "lpt9.har"])
def test_r13_3_nome_reservado_do_windows_ganha_prefixo(reservado: str) -> None:
    assert nome_de_pasta_seguro(reservado) == f"_{reservado}"


def test_r13_3_pasta_da_data_e_hora_sem_dois_pontos(tmp_path: Path) -> None:
    pasta = caminho_do_relatorio(tmp_path, "[::1]:8080", MOMENTO)

    assert pasta.parent.name == "[__1]_8080"
    assert ":" not in pasta.name


def test_r13_4_pasta_existente_para_sem_gravar(tmp_path: Path) -> None:
    pasta = caminho_do_relatorio(tmp_path, "loja.exemplo.com", MOMENTO)
    gravar_relatorio(pasta, {"primeiro": True})

    with pytest.raises(RelatorioJaExiste, match="a pasta da análise já existe"):
        gravar_relatorio(pasta, {"segundo": True})

    with (pasta / "relatorio.json").open(encoding="utf-8") as arquivo:
        assert json.load(arquivo) == {"primeiro": True}


def test_r13_4_mensagem_diz_qual_pasta_ja_existe(tmp_path: Path) -> None:
    pasta = tmp_path / "loja.exemplo.com" / "2026-11-20_14-03-00"
    pasta.mkdir(parents=True)

    with pytest.raises(RelatorioJaExiste) as erro:
        gravar_relatorio(pasta, {})

    assert str(pasta) in str(erro.value)
    assert list(pasta.iterdir()) == []


def test_r17_1_grava_so_o_relatorio_na_pasta_da_analise(tmp_path: Path) -> None:
    pasta = caminho_do_relatorio(tmp_path, "loja.exemplo.com", MOMENTO)

    gravar_relatorio(pasta, {})

    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*")) == [
        "loja.exemplo.com",
        "loja.exemplo.com/2026-11-20_14-03-00",
        "loja.exemplo.com/2026-11-20_14-03-00/relatorio.json",
    ]


def test_r17_1_mantem_as_analises_anteriores_do_site(tmp_path: Path) -> None:
    anterior = caminho_do_relatorio(tmp_path, "loja.exemplo.com", MOMENTO)
    gravar_relatorio(anterior, {"anterior": True})

    gravar_relatorio(caminho_do_relatorio(tmp_path, "loja.exemplo.com", datetime(2026, 11, 27)), {})

    with (anterior / "relatorio.json").open(encoding="utf-8") as arquivo:
        assert json.load(arquivo) == {"anterior": True}
