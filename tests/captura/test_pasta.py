import sys
from datetime import datetime
from pathlib import Path

import pytest

from rastro.captura.pasta import (
    NOME_DO_HAR,
    GravacaoJaExiste,
    UrlInvalida,
    caminho_da_gravacao,
    criar_pasta_da_gravacao,
    desfazer_pasta_da_gravacao,
    host_da_url,
    pasta_padrao_das_gravacoes,
    url_sem_usuario_e_senha,
)

MOMENTO = datetime(2026, 11, 20, 14, 3, 0)


@pytest.mark.parametrize(
    ("url", "host"),
    [
        ("https://Loja.Exemplo.com/produtos?id=1", "loja.exemplo.com"),
        ("http://127.0.0.1:8080/WebGoat/start.mvc", "127.0.0.1:8080"),
        ("https://loja.exemplo.com:443/", "loja.exemplo.com"),
        ("http://loja.exemplo.com:80/", "loja.exemplo.com"),
        ("https://[::1]:8443/", "[::1]:8443"),
    ],
)
def test_r24_2_aceita_url_http_e_https(url: str, host: str) -> None:
    assert host_da_url(url) == host


def test_r24_6_usuario_e_senha_da_url_nao_vao_para_o_host() -> None:
    assert host_da_url("https://ana:segredo@loja.exemplo.com:8443/") == "loja.exemplo.com:8443"


def test_r24_6_url_mostrada_sem_usuario_e_senha() -> None:
    assert (
        url_sem_usuario_e_senha("https://ana:segredo@loja.exemplo.com/painel?x=1")
        == "https://loja.exemplo.com/painel?x=1"
    )
    assert url_sem_usuario_e_senha("https://loja.exemplo.com/") == "https://loja.exemplo.com/"


@pytest.mark.parametrize(
    "url",
    ["loja.exemplo.com", "ftp://loja.exemplo.com", "https://", "", "https://loja.exemplo.com:abc/"],
)
def test_r24_2_recusa_url_sem_http_ou_https(url: str) -> None:
    with pytest.raises(UrlInvalida, match="http:// ou https://"):
        host_da_url(url)


def test_r24_6_pasta_padrao_fica_em_rastro_gravacoes_na_pasta_do_usuario(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert pasta_padrao_das_gravacoes() == tmp_path / "Rastro" / "gravacoes"


def test_r24_6_pasta_por_host_e_data_com_a_porta_trocada(tmp_path: Path) -> None:
    pasta = caminho_da_gravacao(tmp_path, "127.0.0.1:8080", MOMENTO)

    assert pasta == tmp_path / "127.0.0.1_8080" / "2026-11-20_14-03-00"


def test_r24_6_cria_a_pasta_nova_e_devolve_o_caminho_do_har(tmp_path: Path) -> None:
    pasta = tmp_path / "loja.exemplo.com" / "2026-11-20_14-03-00"

    har = criar_pasta_da_gravacao(pasta)

    assert har == pasta / NOME_DO_HAR
    assert pasta.is_dir()
    assert not har.exists()


def test_r24_6_pasta_que_ja_existe_para_sem_tocar_nela(tmp_path: Path) -> None:
    pasta = tmp_path / "loja.exemplo.com" / "2026-11-20_14-03-00"
    pasta.mkdir(parents=True)
    (pasta / NOME_DO_HAR).write_text("anterior", encoding="utf-8")

    with pytest.raises(GravacaoJaExiste, match="já existe"):
        criar_pasta_da_gravacao(pasta)

    assert (pasta / NOME_DO_HAR).read_text(encoding="utf-8") == "anterior"


@pytest.mark.skipif(sys.platform == "win32", reason="permissão de dono só existe no POSIX")
def test_r24_8_so_o_dono_le_a_pasta_da_gravacao(tmp_path: Path) -> None:
    pasta = tmp_path / "loja.exemplo.com" / "2026-11-20_14-03-00"

    criar_pasta_da_gravacao(pasta)

    assert pasta.stat().st_mode & 0o777 == 0o700


def test_r24_4_desfazer_tira_a_pasta_e_o_har_vazio(tmp_path: Path) -> None:
    pasta = tmp_path / "loja.exemplo.com" / "2026-11-20_14-03-00"
    har = criar_pasta_da_gravacao(pasta)
    har.write_text("", encoding="utf-8")

    desfazer_pasta_da_gravacao(pasta)

    assert not pasta.exists()
