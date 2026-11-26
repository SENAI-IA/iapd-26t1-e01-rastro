from dataclasses import replace
from datetime import datetime
from pathlib import Path

import pytest

from rastro.andamento import ANDAMENTO_SILENCIOSO, Andamento
from rastro.comandos import comando_analisar
from rastro.fluxo_da_analise import analisar
from rastro.fontes.completar_cvss import BuscaDeCvss
from rastro.fontes.conector import ConectorDeAvisos
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.ia import escolha_da_ia
from rastro.ia.cliente import ClienteDeIA
from rastro.modelos_da_analise import Analise
from tests.dubles import ConectorFalso, NavegadorFalso, NvdFalso, OsvFalso, RegistroFalso

MOMENTO = datetime(2026, 11, 20, 14, 3, 0)


def analisar_no_momento_fixo(
    caminho_har: Path,
    fonte: ConectorDeAvisos,
    registro: RegistroDePacotes,
    cliente_de_ia: ClienteDeIA | None = None,
    conector_osv: ConectorDeAvisos | None = None,
    busca_de_cvss: BuscaDeCvss | None = None,
    gravado_pelo_rastro: bool = False,
    andamento: Andamento = ANDAMENTO_SILENCIOSO,
) -> Analise:
    analise = analisar(
        caminho_har,
        fonte,
        registro,
        cliente_de_ia,
        conector_osv,
        busca_de_cvss,
        gravado_pelo_rastro=gravado_pelo_rastro,
        andamento=andamento,
    )
    return replace(analise, inicio=MOMENTO)


@pytest.fixture
def navegador(monkeypatch: pytest.MonkeyPatch) -> NavegadorFalso:
    navegador = NavegadorFalso(abre=True)
    monkeypatch.setattr("webbrowser.open", navegador)
    return navegador


@pytest.fixture
def fontes_falsas(monkeypatch: pytest.MonkeyPatch, navegador: NavegadorFalso) -> None:
    monkeypatch.setattr(comando_analisar, "GitHubAdvisory", ConectorFalso)
    monkeypatch.setattr(comando_analisar, "RegistroNpm", RegistroFalso)
    monkeypatch.setattr(comando_analisar, "Osv", OsvFalso)
    monkeypatch.setattr(comando_analisar, "Nvd", NvdFalso)
    monkeypatch.setattr(comando_analisar, "analisar", analisar_no_momento_fixo)


@pytest.fixture
def nenhuma_cli_instalada(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RASTRO_IA", raising=False)
    monkeypatch.setattr(escolha_da_ia.shutil, "which", lambda _nome: None)
