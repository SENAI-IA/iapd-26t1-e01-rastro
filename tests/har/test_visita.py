from datetime import datetime, timedelta, timezone

from rastro.har.modelos import Requisicao
from rastro.har.visita import camada_do_tipo, montar_visita

INICIO = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)


def requisicao(
    indice: int, tipo: str | None, depois_ms: float | None, duracao_ms: float | None = 5.0
) -> Requisicao:
    return Requisicao(
        indice=indice,
        url=f"https://loja.exemplo.com/{indice}",
        metodo="GET",
        status=200,
        tipo_conteudo=tipo,
        cabecalhos_resposta={},
        cookies_resposta=[],
        conteudo=None,
        inicio=None if depois_ms is None else INICIO + timedelta(milliseconds=depois_ms),
        duracao_ms=duracao_ms,
    )


def test_r22_2_visita_conta_o_tempo_desde_a_primeira_requisicao_e_ordena() -> None:
    visita = montar_visita([
        requisicao(0, "text/html", 100),
        requisicao(1, "application/javascript", 350),
        requisicao(2, "text/css", 250),
    ])

    assert [(p.indice_requisicao, p.inicio_ms) for p in visita] == [(0, 0), (2, 150), (1, 250)]


def test_r22_2_visita_ignora_requisicao_sem_horario() -> None:
    visita = montar_visita([requisicao(0, "text/html", 0), requisicao(1, "text/css", None)])

    assert [passo.indice_requisicao for passo in visita] == [0]


def test_r22_2_visita_vazia_quando_o_har_nao_traz_horarios() -> None:
    assert montar_visita([requisicao(0, "text/html", None)]) == []


def test_r22_2_duracao_ausente_vira_zero() -> None:
    assert montar_visita([requisicao(0, "text/html", 0, None)])[0].duracao_ms == 0.0


def test_r22_3_camada_vem_do_tipo_de_conteudo() -> None:
    assert camada_do_tipo("text/html") == "pagina"
    assert camada_do_tipo("application/javascript") == "script"
    assert camada_do_tipo("text/ecmascript") == "script"
    assert camada_do_tipo("text/css") == "estilo"
    assert camada_do_tipo("image/png") == "midia"
    assert camada_do_tipo("application/font-woff2") == "midia"
    assert camada_do_tipo("application/json") == "dados"
    assert camada_do_tipo(None) == "dados"
