import json
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import IO, Any

import pytest

from rastro.har.leitor import (
    MENSAGEM_HAR_INVALIDO,
    HarInvalido,
    HarNaoEncontrado,
    ler_har,
)
from rastro.har.modelos import Cookie, Requisicao

DADOS = Path(__file__).parent.parent / "dados"


def test_r01_1_extrai_a_pagina_e_ignora_as_chaves_com_sublinhado() -> None:
    pagina = ler_har(DADOS / "har-valido.har")[0]

    assert pagina == Requisicao(
        indice=0,
        url="https://loja.exemplo.com.br/",
        metodo="GET",
        status=200,
        tipo_conteudo="text/html",
        cabecalhos_resposta={
            "content-type": "text/html; charset=utf-8",
            "x-frame-options": "DENY",
            "cache-control": "no-store, private",
        },
        cookies_resposta=[
            Cookie(nome="idioma", http_only=False, secure=False, same_site="Lax"),
            Cookie(nome="carrinho", http_only=True, secure=True, same_site="Strict"),
        ],
        conteudo="<html><body>Loja de exemplo</body></html>",
        inicio=datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc),
        duracao_ms=10.0,
    )


def test_r01_1_extrai_todas_as_requisicoes_na_ordem_do_har() -> None:
    requisicoes = ler_har(DADOS / "har-valido.har")

    assert [requisicao.indice for requisicao in requisicoes] == [0, 1, 2]
    assert [requisicao.metodo for requisicao in requisicoes] == ["GET", "GET", "POST"]
    assert requisicoes[1].tipo_conteudo == "application/javascript"
    assert requisicoes[1].conteudo is not None
    assert requisicoes[1].conteudo.startswith("/*! jQuery v3.4.1")


def test_r01_1_cookies_do_har_tem_precedencia_e_nao_guardam_o_valor() -> None:
    entrar = ler_har(DADOS / "har-valido.har")[2]

    assert entrar.cookies_resposta == [
        Cookie(nome="sessao", http_only=True, secure=True, same_site="Strict"),
    ]
    assert "valor-ficticio" not in repr(entrar)


def test_r01_1_set_cookie_fica_so_nos_cookies_sem_o_valor() -> None:
    pagina = ler_har(DADOS / "har-valido.har")[0]

    assert "set-cookie" not in pagina.cabecalhos_resposta
    assert "valor-ficticio" not in repr(pagina)


def test_r01_1_entrada_sem_text_fica_sem_conteudo() -> None:
    websocket = ler_har(DADOS / "har-sem-text.har")[0]

    assert websocket.status == 101
    assert websocket.conteudo is None
    assert websocket.tipo_conteudo == "x-unknown"


def test_r01_2_har_ausente_traz_o_caminho_na_mensagem(tmp_path: Path) -> None:
    caminho = tmp_path / "nao-existe.har"

    with pytest.raises(HarNaoEncontrado) as erro:
        ler_har(caminho)

    assert str(caminho) in str(erro.value)


def test_r01_2_pasta_no_lugar_do_har_conta_como_ausente(tmp_path: Path) -> None:
    with pytest.raises(HarNaoEncontrado):
        ler_har(tmp_path)


def test_r01_3_conteudo_que_nao_e_json_e_har_invalido() -> None:
    with pytest.raises(HarInvalido) as erro:
        ler_har(DADOS / "har-invalido.har")

    assert str(erro.value) == MENSAGEM_HAR_INVALIDO == "o arquivo não é um HAR válido"


def test_r01_3_arquivo_que_nao_e_utf8_e_har_invalido(tmp_path: Path) -> None:
    caminho = tmp_path / "latin1.har"
    caminho.write_bytes('{"log": {"entries": []}, "nome": "ação"}'.encode("latin-1"))

    with pytest.raises(HarInvalido):
        ler_har(caminho)


def entrada_com_resposta(campos: dict[str, object]) -> dict[str, object]:
    return {
        "request": {"url": "https://a.b/", "method": "GET"},
        "response": {"status": 200, **campos},
    }


@pytest.mark.parametrize(
    "conteudo",
    [
        [],
        {},
        {"log": []},
        {"log": {}},
        {"log": {"entries": {}}},
        {"log": {"entries": ["texto"]}},
        {"log": {"entries": [{"request": {"url": "https://a.b/"}, "response": {}}]}},
        {"log": {"entries": [entrada_com_resposta({"content": "texto"})]}},
        {"log": {"entries": [entrada_com_resposta({"headers": {"name": "x"}})]}},
        {"log": {"entries": [entrada_com_resposta({"headers": ["x-frame-options"]})]}},
        {"log": {"entries": [entrada_com_resposta({"cookies": ["sessao=1"]})]}},
    ],
    ids=[
        "lista",
        "sem-log",
        "log-lista",
        "sem-entries",
        "entries-objeto",
        "entrada-texto",
        "entrada-incompleta",
        "content-texto",
        "headers-objeto",
        "headers-com-texto",
        "cookies-com-texto",
    ],
)
def test_r01_3_json_sem_log_entries_validas_e_har_invalido(
    tmp_path: Path, conteudo: object
) -> None:
    caminho = tmp_path / "sem-entries.har"
    caminho.write_text(json.dumps(conteudo), encoding="utf-8")

    with pytest.raises(HarInvalido):
        ler_har(caminho)


def test_r01_1_samesite_que_nao_e_texto_conta_como_ausente(tmp_path: Path) -> None:
    cookie = {"name": "sessao", "httpOnly": True, "secure": True, "sameSite": 1}
    caminho = tmp_path / "cookie.har"
    conteudo = {"log": {"entries": [entrada_com_resposta({"cookies": [cookie]})]}}
    caminho.write_text(json.dumps(conteudo), encoding="utf-8")

    assert ler_har(caminho)[0].cookies_resposta[0].same_site is None


def test_r01_3_har_sem_entradas_e_valido(tmp_path: Path) -> None:
    caminho = tmp_path / "vazio.har"
    caminho.write_text('{"log": {"entries": []}}', encoding="utf-8")

    assert ler_har(caminho) == []


def test_r22_1_le_o_inicio_e_a_duracao_de_cada_requisicao() -> None:
    pagina = ler_har(DADOS / "har-valido.har")[0]

    assert pagina.inicio == datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)
    assert pagina.duracao_ms == 10.0


@pytest.mark.parametrize(
    "horario",
    [
        {},
        {"startedDateTime": 123, "time": "10"},
        {"startedDateTime": "ontem", "time": -1},
        {"startedDateTime": None, "time": True},
    ],
    ids=["ausente", "tipo-errado", "invalido", "nulo-e-booleano"],
)
def test_r22_1_horario_ausente_ou_invalido_fica_vazio_e_o_har_segue(
    tmp_path: Path, horario: dict[str, object]
) -> None:
    caminho = tmp_path / "horario.har"
    conteudo = {"log": {"entries": [{**entrada_com_resposta({}), **horario}]}}
    caminho.write_text(json.dumps(conteudo), encoding="utf-8")

    requisicao = ler_har(caminho)[0]

    assert requisicao.inicio is None
    assert requisicao.duracao_ms is None


def test_r01_4_decodifica_o_conteudo_em_base64() -> None:
    script = ler_har(DADOS / "har-base64.har")[0]

    assert script.conteudo == "/*! jQuery v3.4.1 | (c) JS Foundation */"


def test_r01_4_bytes_fora_do_utf8_viram_caractere_de_substituicao() -> None:
    texto = ler_har(DADOS / "har-base64.har")[1]

    assert texto.conteudo == "ol�"


def test_r01_4_base64_corrompido_fica_sem_conteudo() -> None:
    corrompido = ler_har(DADOS / "har-base64.har")[2]

    assert corrompido.conteudo is None


def test_r01_5_le_o_har_somente_leitura_sem_altera_lo(tmp_path: Path) -> None:
    copia = tmp_path / "har-valido.har"
    shutil.copyfile(DADOS / "har-valido.har", copia)
    copia.chmod(stat.S_IREAD)
    bytes_antes = copia.read_bytes()
    modificado_antes = copia.stat().st_mtime_ns

    requisicoes = ler_har(copia)

    assert len(requisicoes) == 3
    assert copia.read_bytes() == bytes_antes
    assert copia.stat().st_mtime_ns == modificado_antes


def test_r01_5_abre_o_har_so_no_modo_de_leitura(monkeypatch: pytest.MonkeyPatch) -> None:
    modos_usados: list[str] = []
    abrir_original = Path.open

    def abrir_registrando(caminho: Path, modo: str = "r", **opcoes: Any) -> IO[Any]:
        modos_usados.append(modo)
        return abrir_original(caminho, modo, **opcoes)

    monkeypatch.setattr(Path, "open", abrir_registrando)

    ler_har(DADOS / "har-valido.har")

    assert modos_usados == ["r"]


def test_r01_7_guarda_a_url_da_pagina_quando_o_titulo_e_uma_url(tmp_path: Path) -> None:
    caminho = tmp_path / "paginas.har"
    entrada = {
        "request": {"url": "https://www.google.com/rmkt/collect/1/", "method": "GET"},
        "response": {"status": 200, "headers": [], "cookies": [], "content": {}},
    }
    caminho.write_text(
        json.dumps(
            {
                "log": {
                    "pages": [
                        {"id": "page_1", "title": "https://cursos.exemplo.org.br/"},
                        {"id": "page_2", "title": "Cursos de exemplo"},
                    ],
                    "entries": [
                        {**entrada, "pageref": "page_1"},
                        {**entrada, "pageref": "page_2"},
                        entrada,
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    requisicoes = ler_har(caminho)

    assert [requisicao.url_da_pagina for requisicao in requisicoes] == [
        "https://cursos.exemplo.org.br/",
        None,
        None,
    ]
