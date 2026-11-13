import json
import shutil
import signal
import subprocess
import sys
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from rastro import cli
from rastro.captura.playwright import NavegadorAusente, PlaywrightAusente
from rastro.captura.sessao import FalhaAoNavegar
from rastro.cli import AVISO_SEM_IA, executar
from rastro.fluxo import Analise, analisar
from rastro.fontes.conector import ConectorDeAvisos
from rastro.fontes.nvd import BuscaDeCvss
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.ia import cliente
from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.relatorio.html import TAG_DOS_DADOS_VAZIA
from tests.dubles import (
    DADOS,
    HAR_DA_LOJA,
    HAR_DO_JUICE_SHOP,
    TRECHO_DO_ANGULAR,
    ConectorFalso,
    NvdFalso,
    OsvFalso,
    ProvedorFalso,
    RegistroFalso,
)

MOMENTO = datetime(2026, 11, 20, 14, 3, 0)
PASTA_DA_LOJA = Path("loja.exemplo.com") / "2026-11-20_14-03-00"


def analisar_no_momento_fixo(
    caminho_har: Path,
    fonte: ConectorDeAvisos,
    registro: RegistroDePacotes,
    ia: ClienteDeIA | None = None,
    osv: ConectorDeAvisos | None = None,
    nvd: BuscaDeCvss | None = None,
    gravado_pelo_rastro: bool = False,
) -> Analise:
    analise = analisar(
        caminho_har, fonte, registro, ia, osv, nvd, gravado_pelo_rastro=gravado_pelo_rastro
    )
    return replace(analise, inicio=MOMENTO)


class NavegadorFalso:
    def __init__(self, abre: bool) -> None:
        self.abre = abre
        self.enderecos: list[str] = []

    def __call__(self, endereco: str) -> bool:
        self.enderecos.append(endereco)
        return self.abre


@pytest.fixture
def navegador(monkeypatch: pytest.MonkeyPatch) -> NavegadorFalso:
    navegador = NavegadorFalso(abre=True)
    monkeypatch.setattr("webbrowser.open", navegador)
    return navegador


@pytest.fixture
def fontes_falsas(monkeypatch: pytest.MonkeyPatch, navegador: NavegadorFalso) -> None:
    monkeypatch.setattr(cli, "GitHubAdvisory", ConectorFalso)
    monkeypatch.setattr(cli, "RegistroNpm", RegistroFalso)
    monkeypatch.setattr(cli, "Osv", OsvFalso)
    monkeypatch.setattr(cli, "Nvd", NvdFalso)
    monkeypatch.setattr(cli, "analisar", analisar_no_momento_fixo)


def analisar_loja(saida: Path) -> int:
    return executar(["analisar", str(HAR_DA_LOJA), "--sem-ia", "--saida", str(saida)])


def ler_relatorio(caminho: Path) -> dict[str, Any]:
    with caminho.open(encoding="utf-8") as arquivo:
        dados: dict[str, Any] = json.load(arquivo)
    return dados


def test_r14_7_ajuda_abre_e_retorna_0(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as saida:
        executar(["--help"])

    assert saida.value.code == 0
    assert "usage: rastro" in capsys.readouterr().out


def test_r14_7_sem_argumentos_mostra_a_ajuda_e_retorna_0(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert executar([]) == 0
    assert "HAR" in capsys.readouterr().out


def test_r18_1_comando_rastro_sai_com_o_codigo_da_execucao(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "executar", lambda: 1)

    with pytest.raises(SystemExit) as saida:
        cli.principal()

    assert saida.value.code == 1


def test_r14_7_python_m_rastro_help_retorna_0() -> None:
    resultado = subprocess.run(
        [sys.executable, "-m", "rastro", "--help"],
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )

    assert resultado.returncode == 0
    assert "usage: rastro" in resultado.stdout
    assert "analisar" in resultado.stdout


def test_r14_7_ajuda_descreve_sem_ia_e_o_que_se_perde_na_mesma_linha(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "200")

    with pytest.raises(SystemExit):
        executar(["analisar", "--help"])

    linhas = capsys.readouterr().out.splitlines()
    linha_da_opcao = next(linha for linha in linhas if linha.strip().startswith("--sem-ia"))
    assert "não procura bibliotecas em bundles e não explica os achados" in linha_da_opcao


def test_r23_8_como_usar_aparece_na_ajuda(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        executar(["--help"])

    assert "como-usar" in capsys.readouterr().out


def test_r23_8_como_usar_abre_o_modelo_sem_dados_no_navegador(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    navegador = NavegadorFalso(abre=True)
    monkeypatch.setattr(cli.webbrowser, "open", navegador)

    assert executar(["como-usar"]) == 0

    modelo = Path(cli.__file__).parent / "relatorio" / "modelo.html"
    assert navegador.enderecos == [modelo.resolve().as_uri()]
    assert TAG_DOS_DADOS_VAZIA in modelo.read_text(encoding="utf-8")
    assert str(modelo.resolve()) in capsys.readouterr().out


def test_r23_8_como_usar_sem_navegador_mostra_o_caminho_e_retorna_0(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cli.webbrowser, "open", NavegadorFalso(abre=False))

    assert executar(["como-usar"]) == 0

    saida = capsys.readouterr().out
    assert "Não foi possível abrir o navegador" in saida
    assert "modelo.html" in saida


def test_r23_8_como_usar_nao_grava_nada(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli.webbrowser, "open", NavegadorFalso(abre=True))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.chdir(tmp_path)

    executar(["como-usar"])

    assert list(tmp_path.iterdir()) == []


def test_r23_8_como_usar_nao_deixa_o_navegador_escrever_no_terminal(
    capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def navegador_que_avisa(endereco: str) -> bool:
        subprocess.run(
            [sys.executable, "-c", "import sys; print('aviso'); print('erro', file=sys.stderr)"],
            check=True,
        )
        return True

    monkeypatch.setattr("webbrowser.open", navegador_que_avisa)

    executar(["como-usar"])

    saida = capfd.readouterr()
    assert "aviso" not in saida.out
    assert "erro" not in saida.err
    assert "aberto no navegador" in saida.out


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_1_analisar_sem_ia_grava_o_json_na_pasta_da_analise(tmp_path: Path) -> None:
    assert analisar_loja(tmp_path) == 0

    relatorio = ler_relatorio(tmp_path / PASTA_DA_LOJA / "relatorio.json")
    assert relatorio["versao_formato"] == 1
    assert relatorio["resumo"]
    assert relatorio["analise"]["limitacoes"]
    assert (tmp_path / PASTA_DA_LOJA / "relatorio.html").is_file()


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_2_sem_saida_grava_em_rastro_relatorios_na_pasta_do_usuario(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert executar(["analisar", str(HAR_DA_LOJA), "--sem-ia"]) == 0

    assert (tmp_path / "Rastro" / "relatorios" / PASTA_DA_LOJA / "relatorio.json").is_file()


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_3_har_sem_site_usa_o_nome_do_har(tmp_path: Path) -> None:
    har = DADOS / "har-sem-text.har"
    pasta_esperada = tmp_path / "saida" / "har-sem-text" / "2026-11-20_14-03-00"

    assert executar(["analisar", str(har), "--sem-ia", "--saida", str(tmp_path / "saida")]) == 0

    assert (pasta_esperada / "relatorio.json").is_file()


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_4_pasta_da_analise_existente_encerra_com_1_sem_gravar(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    pasta = tmp_path / PASTA_DA_LOJA
    pasta.mkdir(parents=True)

    assert analisar_loja(tmp_path) == 1

    assert list(pasta.iterdir()) == []
    erro = capsys.readouterr().err
    assert "a pasta da análise já existe" in erro
    assert str(pasta) in erro


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_8_mostra_a_pasta_o_html_o_json_e_o_resumo_de_uma_linha(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    analisar_loja(tmp_path)

    saida = capsys.readouterr().out
    assert f"Relatório gravado em: {tmp_path / PASTA_DA_LOJA}" in saida
    assert f"HTML: {tmp_path / PASTA_DA_LOJA / 'relatorio.html'}" in saida
    assert f"JSON: {tmp_path / PASTA_DA_LOJA / 'relatorio.json'}" in saida
    assert (
        "Resumo: loja.exemplo.com · bibliotecas: 2 (1 com falhas) · achados: 2"
        " · nota máxima: 8,3 · ações: 7 (1 alta, 3 média, 3 baixa, 0 a avaliar)"
    ) in saida


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_analisar_abre_o_relatorio_html_no_navegador(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, navegador: NavegadorFalso
) -> None:
    assert analisar_loja(tmp_path) == 0

    html = tmp_path / PASTA_DA_LOJA / "relatorio.html"
    assert navegador.enderecos == [html.resolve().as_uri()]
    assert "Relatório aberto no navegador." in capsys.readouterr().out


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_nao_abrir_grava_sem_abrir_o_navegador(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, navegador: NavegadorFalso
) -> None:
    argumentos = ["analisar", str(HAR_DA_LOJA), "--sem-ia", "--saida", str(tmp_path)]

    assert executar([*argumentos, "--nao-abrir"]) == 0

    assert navegador.enderecos == []
    assert (tmp_path / PASTA_DA_LOJA / "relatorio.html").is_file()
    assert "navegador" not in capsys.readouterr().out


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_sem_navegador_avisa_mantem_o_caminho_e_retorna_0(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, navegador: NavegadorFalso
) -> None:
    navegador.abre = False

    assert analisar_loja(tmp_path) == 0

    saida = capsys.readouterr().out
    assert "Não foi possível abrir o navegador" in saida
    assert f"HTML: {tmp_path / PASTA_DA_LOJA / 'relatorio.html'}" in saida


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_9_analisar_nao_deixa_o_navegador_escrever_no_terminal(
    capfd: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def navegador_que_avisa(endereco: str) -> bool:
        subprocess.run(
            [sys.executable, "-c", "import sys; print('aviso'); print('erro', file=sys.stderr)"],
            check=True,
        )
        return True

    monkeypatch.setattr("webbrowser.open", navegador_que_avisa)

    analisar_loja(tmp_path)

    saida = capfd.readouterr()
    assert "aviso" not in saida.out.splitlines()
    assert "erro" not in saida.err.splitlines()
    assert "Relatório aberto no navegador." in saida.out


@pytest.mark.usefixtures("fontes_falsas")
def test_r14_5_sem_ia_avisa_no_terminal_no_inicio_e_no_fim(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    analisar_loja(tmp_path)

    linhas = capsys.readouterr().out.splitlines()
    assert linhas[0] == AVISO_SEM_IA
    assert linhas[-1] == AVISO_SEM_IA
    assert any("sem explicação em linguagem simples" in linha for linha in linhas)
    assert any("são os mesmos de uma análise com IA" in linha for linha in linhas)


@pytest.mark.usefixtures("fontes_falsas")
def test_r13_8_resumo_sem_achados_fala_sem_nota(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    har = DADOS / "har-sem-text.har"
    executar(["analisar", str(har), "--sem-ia", "--saida", str(tmp_path)])

    assert "nota máxima: sem nota" in capsys.readouterr().out


@pytest.fixture
def clis_procuradas(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    procuradas: list[str] = []

    def which_falso(nome: str) -> str:
        procuradas.append(nome)
        return f"/usr/local/bin/{nome}"

    monkeypatch.delenv("RASTRO_IA", raising=False)
    monkeypatch.setattr(cliente.shutil, "which", which_falso)
    return procuradas


@pytest.fixture
def nenhuma_cli_instalada(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RASTRO_IA", raising=False)
    monkeypatch.setattr(cliente.shutil, "which", lambda _nome: None)


class ProvedoresFalsos:
    def __init__(self) -> None:
        self.respostas: list[RespostaDoProvedor | FalhaDoProvedor] = [
            FalhaDoProvedor("o dublê não responde")
        ]
        self.criados: list[tuple[ProvedorFalso, str]] = []

    def fabrica(self, nome: str) -> Callable[[str], ProvedorFalso]:
        def criar(executavel: str) -> ProvedorFalso:
            provedor = ProvedorFalso(self.respostas, nome=nome)
            self.criados.append((provedor, executavel))
            return provedor

        return criar


@pytest.fixture
def provedores(monkeypatch: pytest.MonkeyPatch) -> ProvedoresFalsos:
    falsos = ProvedoresFalsos()
    fabricas = {nome: falsos.fabrica(nome) for nome in cli.PROVEDORES_DAS_IAS}
    monkeypatch.setattr(cli, "PROVEDORES_DAS_IAS", fabricas)
    return falsos


def analisar_com_ia(har: Path, saida: Path, *opcoes: str) -> int:
    return executar(["analisar", str(har), *opcoes, "--saida", str(saida)])


def test_r14_1_cada_ia_tem_o_seu_provedor() -> None:
    assert set(cli.PROVEDORES_DAS_IAS) == set(cliente.EXECUTAVEIS_DAS_IAS)


@pytest.mark.usefixtures("fontes_falsas")
def test_r14_1_sem_ia_e_sem_variavel_usa_o_kiro_com_o_executavel_achado(
    tmp_path: Path, clis_procuradas: list[str], provedores: ProvedoresFalsos
) -> None:
    assert analisar_com_ia(HAR_DA_LOJA, tmp_path) == 0

    assert clis_procuradas == ["kiro-cli"]
    [(provedor, executavel)] = provedores.criados
    assert (provedor.nome, executavel) == ("kiro", "/usr/local/bin/kiro-cli")


@pytest.mark.usefixtures("fontes_falsas")
def test_r14_1_variavel_rastro_ia_escolhe_a_ia(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    clis_procuradas: list[str],
    provedores: ProvedoresFalsos,
) -> None:
    monkeypatch.setenv("RASTRO_IA", "codex")

    analisar_com_ia(HAR_DA_LOJA, tmp_path)

    assert clis_procuradas == ["codex"]
    assert [provedor.nome for provedor, _ in provedores.criados] == ["codex"]


@pytest.mark.usefixtures("fontes_falsas")
def test_r14_1_opcao_ia_vale_antes_da_variavel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    clis_procuradas: list[str],
    provedores: ProvedoresFalsos,
) -> None:
    monkeypatch.setenv("RASTRO_IA", "codex")

    analisar_com_ia(HAR_DA_LOJA, tmp_path, "--ia", "claude")

    assert clis_procuradas == ["claude"]
    assert [provedor.nome for provedor, _ in provedores.criados] == ["claude"]


@pytest.mark.usefixtures("fontes_falsas", "clis_procuradas")
def test_r14_8_com_ia_explica_os_achados_e_grava_provedor_e_chamadas_no_json(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, provedores: ProvedoresFalsos
) -> None:
    gravada = (DADOS / "kiro-explicacao-jquery.txt").read_text(encoding="utf-8")
    provedores.respostas = [RespostaDoProvedor(gravada, None)]

    assert analisar_com_ia(HAR_DA_LOJA, tmp_path) == 0

    relatorio = ler_relatorio(tmp_path / PASTA_DA_LOJA / "relatorio.json")
    assert relatorio["analise"]["ia"] == "kiro"
    assert relatorio["analise"]["limitacoes"] == []
    jquery = relatorio["bibliotecas"][0]
    assert jquery["explicacao"]["gerada_por_ia"] is True
    assert [chamada["etapa"] for chamada in relatorio["ia"]["chamadas"]] == ["explicar_achado"]
    assert relatorio["ia"]["chamadas"][0]["sucesso"] is True
    saida = capsys.readouterr().out
    assert saida.startswith("Análise com a IA kiro.")
    assert AVISO_SEM_IA not in saida


@pytest.mark.usefixtures("fontes_falsas", "clis_procuradas")
def test_r03_1_com_ia_procura_bibliotecas_em_bundles(
    tmp_path: Path, provedores: ProvedoresFalsos
) -> None:
    angular = {"pacote": "@angular/core", "versao": "22.2.2", "trecho": TRECHO_DO_ANGULAR}
    provedores.respostas = [
        RespostaDoProvedor(json.dumps({"bibliotecas": [angular]}), None),
        FalhaDoProvedor("sem resposta"),
    ]

    assert analisar_com_ia(HAR_DO_JUICE_SHOP, tmp_path) == 0

    [relatorio_json] = tmp_path.rglob("relatorio.json")
    relatorio = ler_relatorio(relatorio_json)
    assert [(b["pacote"], b["metodo"]) for b in relatorio["bibliotecas"]] == [
        ("@angular/core", "ia")
    ]
    assert relatorio["resumo"]["encontradas_so_pela_ia"] == 1
    assert [chamada["sucesso"] for chamada in relatorio["ia"]["chamadas"]] == [True, False]


@pytest.mark.usefixtures("fontes_falsas", "clis_procuradas")
def test_r07_3_falha_da_ia_nao_derruba_a_analise(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, provedores: ProvedoresFalsos
) -> None:
    assert analisar_com_ia(HAR_DA_LOJA, tmp_path) == 0

    relatorio = ler_relatorio(tmp_path / PASTA_DA_LOJA / "relatorio.json")
    assert relatorio["bibliotecas"][0]["explicacao"]["gerada_por_ia"] is False
    assert relatorio["ia"]["chamadas"][0]["resposta"] == "o dublê não responde"
    [limitacao] = relatorio["analise"]["limitacoes"]
    assert limitacao["id"] == "ia_falhou_explicacao"
    assert limitacao["texto"].startswith("A IA (kiro) falhou em 1 de 1 chamadas para explicar")
    assert f"Atenção: {limitacao['texto']}" in capsys.readouterr().out


@pytest.mark.usefixtures("fontes_falsas", "clis_procuradas")
def test_r03_5_falha_da_ia_nos_bundles_avisa_que_ficaram_sem_analise(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, provedores: ProvedoresFalsos
) -> None:
    provedores.respostas = [FalhaDoProvedor("sem resposta"), FalhaDoProvedor("sem resposta")]

    assert analisar_com_ia(HAR_DO_JUICE_SHOP, tmp_path) == 0

    [relatorio_json] = tmp_path.rglob("relatorio.json")
    limitacoes = ler_relatorio(relatorio_json)["analise"]["limitacoes"]
    assert [limitacao["id"] for limitacao in limitacoes] == ["ia_falhou_identificacao"]
    assert "procurar bibliotecas em bundles" in limitacoes[0]["texto"]
    assert "Atenção: A IA (kiro) falhou" in capsys.readouterr().out


@pytest.mark.usefixtures("provedores")
def test_r14_2_ia_invalida_encerra_com_1_listando_as_opcoes(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, clis_procuradas: list[str]
) -> None:
    resultado = analisar_com_ia(HAR_DA_LOJA, tmp_path, "--ia", "gpt")

    assert resultado == 1
    assert "Opções válidas: kiro, claude, codex." in capsys.readouterr().err
    assert clis_procuradas == []
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("provedores")
def test_r14_2_rastro_ia_invalida_encerra_com_1(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    clis_procuradas: list[str],
) -> None:
    monkeypatch.setenv("RASTRO_IA", "gemini")

    assert analisar_com_ia(HAR_DA_LOJA, tmp_path) == 1

    assert "RASTRO_IA" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("nenhuma_cli_instalada")
def test_r14_3_cli_ausente_encerra_com_1_antes_de_ler_o_har(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, provedores: ProvedoresFalsos
) -> None:
    har_que_nao_existe = tmp_path / "nao-existe.har"

    assert analisar_com_ia(har_que_nao_existe, tmp_path) == 1

    erro = capsys.readouterr().err
    assert "kiro-cli" in erro
    assert "--sem-ia" in erro
    assert "não procura bibliotecas em bundles e não explica os achados" in erro
    assert str(har_que_nao_existe) not in erro
    assert provedores.criados == []


@pytest.mark.usefixtures("fontes_falsas", "nenhuma_cli_instalada")
def test_r14_5_sem_ia_nao_procura_a_cli_nem_confere_rastro_ia(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("RASTRO_IA", "gemini")

    assert analisar_loja(tmp_path) == 0


@pytest.mark.usefixtures("fontes_falsas")
def test_r01_2_har_inexistente_encerra_com_1_e_mostra_o_caminho(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    caminho = tmp_path / "nao-existe.har"

    assert executar(["analisar", str(caminho), "--sem-ia", "--saida", str(tmp_path)]) == 1

    assert str(caminho) in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("fontes_falsas")
def test_r01_3_har_invalido_encerra_com_1_sem_relatorio(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    har = DADOS / "har-invalido.har"

    assert executar(["analisar", str(har), "--sem-ia", "--saida", str(tmp_path)]) == 1

    assert "o arquivo não é um HAR válido" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


@pytest.mark.usefixtures("fontes_falsas")
def test_r17_1_grava_so_o_relatorio_e_nao_altera_o_har(tmp_path: Path) -> None:
    antes = HAR_DA_LOJA.read_bytes()

    analisar_loja(tmp_path)

    arquivos = sorted(p for p in tmp_path.rglob("*") if p.is_file())
    assert arquivos == [
        tmp_path / PASTA_DA_LOJA / "relatorio.html",
        tmp_path / PASTA_DA_LOJA / "relatorio.json",
    ]
    assert HAR_DA_LOJA.read_bytes() == antes


class SessaoFalsa:
    def __init__(
        self, requisicoes: int = 3, falha_ao_ir: str | None = None, ctrl_c: bool = False
    ) -> None:
        self.requisicoes = requisicoes
        self.scripts = 1
        self.falha_ao_ir = falha_ao_ir
        self.ctrl_c = ctrl_c
        self.urls: list[str] = []
        self.esperas = 0
        self.urls_antes_de_fechar = 1

    def ir(self, url: str) -> None:
        self.urls.append(url)
        if self.falha_ao_ir is not None:
            raise FalhaAoNavegar(self.falha_ao_ir)

    def links(self) -> list[str]:
        return []

    def endereco(self) -> str:
        return self.urls[-1] if self.urls else ""

    def aberta(self) -> bool:
        return self.esperas < 1000

    def esperar(self, segundos: float) -> None:
        self.esperas += 1
        if self.ctrl_c:
            signal.raise_signal(signal.SIGINT)
        elif self.esperas >= 2 and len(self.urls) >= self.urls_antes_de_fechar:
            self.esperas = 1000


class GravacaoFalsa:
    def __init__(self) -> None:
        self.sessao = SessaoFalsa()
        self.hars: list[Path] = []
        self.grava_o_har = True
        self.har_de_origem = HAR_DA_LOJA
        self.erro: Exception | None = None

    @contextmanager
    def __call__(self, har: Path) -> Iterator[SessaoFalsa]:
        self.hars.append(har)
        if self.erro is not None:
            raise self.erro
        try:
            yield self.sessao
        finally:
            if self.grava_o_har:
                shutil.copyfile(self.har_de_origem, har)


@pytest.fixture
def gravacao(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, fontes_falsas: None) -> GravacaoFalsa:
    falsa = GravacaoFalsa()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(cli, "conferir_playwright", lambda: None)
    monkeypatch.setattr(cli, "abrir_gravacao", falsa)
    return falsa


def gravar_loja(saida: Path, *opcoes: str) -> int:
    return executar(["gravar", "https://loja.exemplo.com/", "--saida", str(saida), *opcoes])


def pastas_das_gravacoes(raiz: Path) -> list[Path]:
    return sorted((raiz / "Rastro" / "gravacoes").glob("*/*"))


def test_r24_1_gravar_aparece_na_ajuda(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        executar(["--help"])

    assert "gravar" in capsys.readouterr().out


def test_r24_7_grava_a_visita_e_analisa_o_har_gravado(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--sem-ia", "--nao-abrir") == 0

    assert gravacao.sessao.urls == ["https://loja.exemplo.com/"]
    [pasta] = pastas_das_gravacoes(tmp_path)
    assert pasta.parent.name == "loja.exemplo.com"
    assert gravacao.hars == [pasta / "visita.har"]
    relatorio = ler_relatorio(saida / PASTA_DA_LOJA / "relatorio.json")
    assert relatorio["analise"]["har"] == "visita.har"
    terminal = capsys.readouterr().out
    assert f"Visita gravada em: {pasta / 'visita.har'}" in terminal
    assert "feche a janela quando terminar" in terminal


def test_r24_2_url_sem_http_encerra_com_1_sem_abrir_o_navegador(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    assert executar(["gravar", "loja.exemplo.com", "--sem-ia"]) == 1

    assert "http:// ou https://" in capsys.readouterr().err
    assert gravacao.hars == []
    assert pastas_das_gravacoes(tmp_path) == []


def test_r24_3_sem_playwright_encerra_com_1_antes_de_criar_a_pasta(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    gravacao: GravacaoFalsa,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def sem_playwright() -> None:
        raise PlaywrightAusente()

    monkeypatch.setattr(cli, "conferir_playwright", sem_playwright)

    assert gravar_loja(tmp_path, "--sem-ia") == 1

    assert "pip install playwright" in capsys.readouterr().err
    assert gravacao.hars == []
    assert pastas_das_gravacoes(tmp_path) == []


def test_r24_4_sem_chrome_nem_edge_encerra_com_1_e_tira_a_pasta_vazia(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.erro = NavegadorAusente()

    assert gravar_loja(tmp_path, "--sem-ia") == 1

    assert "Chrome" in capsys.readouterr().err
    assert pastas_das_gravacoes(tmp_path) == []


@pytest.mark.usefixtures("nenhuma_cli_instalada")
def test_r24_5_cli_da_ia_ausente_encerra_com_1_antes_de_abrir_o_navegador(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    assert gravar_loja(tmp_path) == 1

    erro = capsys.readouterr().err
    assert "kiro-cli" in erro
    assert "--sem-ia" in erro
    assert gravacao.hars == []


def test_r24_7_sem_nenhuma_requisicao_encerra_com_1_sem_relatorio(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.sessao = SessaoFalsa(requisicoes=0)
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--sem-ia") == 1

    assert "nenhuma requisição foi gravada" in capsys.readouterr().err
    assert not saida.exists()


def test_r24_7_har_que_nao_foi_gravado_encerra_com_1_sem_relatorio(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.grava_o_har = False
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--sem-ia") == 1

    assert "antes de gravar o HAR" in capsys.readouterr().err
    assert not saida.exists()


def test_r24_7_ctrl_c_encerra_a_gravacao_e_analisa_o_que_foi_gravado(
    tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.sessao = SessaoFalsa(ctrl_c=True)
    tratador_original = signal.getsignal(signal.SIGINT)
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--sem-ia", "--nao-abrir") == 0

    assert gravacao.sessao.esperas == 1
    assert (saida / PASTA_DA_LOJA / "relatorio.json").is_file()
    assert signal.getsignal(signal.SIGINT) is tratador_original


def test_r24_1_falha_na_primeira_pagina_avisa_e_continua_gravando(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.sessao = SessaoFalsa(falha_ao_ir="net::ERR_CONNECTION_REFUSED")

    assert gravar_loja(tmp_path / "relatorios", "--sem-ia", "--nao-abrir") == 0

    assert "ERR_CONNECTION_REFUSED" in capsys.readouterr().out


def test_r24_8_avisa_que_o_har_gravado_guarda_a_sessao(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravar_loja(tmp_path / "relatorios", "--sem-ia", "--nao-abrir")

    terminal = capsys.readouterr().out
    assert "guarda a sessão do site" in terminal
    assert "Não compartilhe o arquivo" in terminal


def test_r24_9_sem_cookies_na_gravacao_nao_pede_o_har_completo(
    tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.har_de_origem = DADOS / "har-sem-text.har"
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--sem-ia", "--nao-abrir") == 0

    [json_do_relatorio] = saida.glob("*/*/relatorio.json")
    checagens = ler_relatorio(json_do_relatorio)["checagens"]
    de_cookie = [c for c in checagens if c["id"] in ("C06", "C07", "C08")]
    assert [c["situacao"] for c in de_cookie] == ["nao_verificada"] * 3
    assert all("não criou nenhum cookie" in c["detalhe"] for c in de_cookie)
    assert not any("HAR completo" in c["detalhe"] for c in de_cookie)


@pytest.fixture
def enter(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    lidos: list[str] = []

    def apertar_enter() -> str:
        lidos.append("")
        return ""

    monkeypatch.setattr(cli, "ler_enter", apertar_enter)
    return lidos


@pytest.mark.usefixtures("enter")
def test_r24_14_robo_mostra_o_progresso_e_por_que_parou(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.sessao.urls_antes_de_fechar = 2
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--robo", "--sem-ia", "--nao-abrir") == 0

    terminal = capsys.readouterr().out
    assert "O robô vai navegar pelos links de loja.exemplo.com" in terminal
    assert "páginas 1/20 · requisições 3 · scripts 1" in terminal
    assert "O robô parou: nenhum link novo" in terminal
    assert (saida / PASTA_DA_LOJA / "relatorio.json").is_file()


def test_r24_10_robo_avisa_sobre_login_e_espera_o_enter(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    gravacao: GravacaoFalsa,
    enter: list[str],
) -> None:
    gravacao.sessao.urls_antes_de_fechar = 2

    assert gravar_loja(tmp_path / "relatorios", "--robo", "--sem-ia", "--nao-abrir") == 0

    terminal = capsys.readouterr().out
    assert enter == [""]
    assert terminal.index("entre agora na janela aberta") < terminal.index("O robô vai navegar")
    assert "Cuidado em sistema de produção" in terminal
    assert "grave sem --robo e navegue você mesmo" in terminal


@pytest.mark.usefixtures("enter")
def test_r24_15_depois_do_robo_a_janela_fica_aberta_ate_fechar(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.sessao.urls_antes_de_fechar = 2

    assert gravar_loja(tmp_path / "relatorios", "--robo", "--sem-ia", "--nao-abrir") == 0

    terminal = capsys.readouterr().out
    assert terminal.index("O robô parou") < terminal.index("A janela continua aberta")
    assert gravacao.sessao.esperas == 1000
    assert gravacao.sessao.urls == ["https://loja.exemplo.com/"] * 2


def test_r24_10_ctrl_c_antes_do_enter_nao_roda_o_robo_e_analisa(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    gravacao: GravacaoFalsa,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sem_enter = threading.Event()

    def nunca_aperta() -> str:
        sem_enter.wait(5)
        return ""

    monkeypatch.setattr(cli, "ler_enter", nunca_aperta)
    gravacao.sessao = SessaoFalsa(ctrl_c=True)
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--robo", "--sem-ia", "--nao-abrir") == 0

    sem_enter.set()
    assert "O robô vai navegar" not in capsys.readouterr().out
    assert gravacao.sessao.urls == ["https://loja.exemplo.com/"]
    assert (saida / PASTA_DA_LOJA / "relatorio.json").is_file()
