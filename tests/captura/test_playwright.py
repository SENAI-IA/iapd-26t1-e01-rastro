import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Error

from rastro.captura.playwright import (
    VERSAO_DO_PLAYWRIGHT,
    NavegadorAusente,
    NavegadorNaoAbriu,
    PlaywrightAusente,
    abrir_gravacao,
    abrir_navegador_da_maquina,
    conferir_playwright,
)

NAVEGADOR_ABERTO = object()


def nao_encontrado(canal: str) -> Error:
    return Error(f"BrowserType.launch: Chromium distribution '{canal}' is not found at /opt/x")


class ChromiumFalso:
    def __init__(self, instalados: set[str], erro_ao_abrir: Error | None = None) -> None:
        self.instalados = instalados
        self.erro_ao_abrir = erro_ao_abrir
        self.chamadas: list[dict[str, Any]] = []

    def launch(self, **opcoes: Any) -> object:
        self.chamadas.append(opcoes)
        if self.erro_ao_abrir is not None:
            raise self.erro_ao_abrir
        if opcoes["channel"] not in self.instalados:
            raise nao_encontrado(opcoes["channel"])
        return NAVEGADOR_ABERTO


class PlaywrightFalso:
    def __init__(self, chromium: ChromiumFalso) -> None:
        self.chromium = chromium


def test_r24_3_sem_playwright_mostra_o_comando_de_instalacao_neste_python(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)

    with pytest.raises(PlaywrightAusente) as erro:
        conferir_playwright()

    mensagem = str(erro.value)
    assert f'"{sys.executable}" -m pip install playwright=={VERSAO_DO_PLAYWRIGHT}' in mensagem
    assert "funciona sem ele" in mensagem


def test_r24_3_com_playwright_instalado_nao_reclama() -> None:
    conferir_playwright()


def test_r24_1_abre_o_chrome_da_maquina_com_janela_e_sem_tratar_o_ctrl_c() -> None:
    chromium = ChromiumFalso(instalados={"chrome", "msedge"})

    navegador = abrir_navegador_da_maquina(PlaywrightFalso(chromium))  # type: ignore[arg-type]

    assert navegador is NAVEGADOR_ABERTO
    assert chromium.chamadas == [{"channel": "chrome", "headless": False, "handle_sigint": False}]


def test_r24_1_sem_chrome_abre_o_edge() -> None:
    chromium = ChromiumFalso(instalados={"msedge"})

    navegador = abrir_navegador_da_maquina(PlaywrightFalso(chromium))  # type: ignore[arg-type]

    assert navegador is NAVEGADOR_ABERTO
    assert [chamada["channel"] for chamada in chromium.chamadas] == ["chrome", "msedge"]


def test_r24_4_sem_chrome_nem_edge_pede_para_instalar_um_dos_dois() -> None:
    chromium = ChromiumFalso(instalados=set())

    with pytest.raises(NavegadorAusente, match="não baixa navegador"):
        abrir_navegador_da_maquina(PlaywrightFalso(chromium))  # type: ignore[arg-type]


def test_r24_4_outro_erro_ao_abrir_o_navegador_nao_vira_navegador_ausente() -> None:
    chromium = ChromiumFalso(instalados={"chrome"}, erro_ao_abrir=Error("Target crashed"))

    with pytest.raises(Error, match="Target crashed"):
        abrir_navegador_da_maquina(PlaywrightFalso(chromium))  # type: ignore[arg-type]


SEM_TELA = Error(
    "BrowserType.launch: Target page, context or browser has been closed\n"
    "Looks like you launched a headed browser without having a XServer running."
)


def test_r24_4_navegador_que_nao_abre_vira_erro_com_a_mensagem_pronta(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    chromium = ChromiumFalso(instalados={"chrome"}, erro_ao_abrir=SEM_TELA)

    @contextmanager
    def sync_playwright_falso() -> Iterator[PlaywrightFalso]:
        yield PlaywrightFalso(chromium)

    monkeypatch.setattr("playwright.sync_api.sync_playwright", sync_playwright_falso)

    with pytest.raises(NavegadorNaoAbriu) as erro, abrir_gravacao(tmp_path / "visita.har"):
        pass

    assert str(erro.value) == (
        "não foi possível abrir o navegador para gravar a visita: "
        "BrowserType.launch: Target page, context or browser has been closed"
    )
