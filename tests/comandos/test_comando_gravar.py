import shutil
import signal
import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from rastro.captura.playwright import NavegadorAusente, NavegadorNaoAbriu, PlaywrightAusente
from rastro.captura.sessao import FalhaAoNavegar
from rastro.cli import executar
from rastro.comandos import comando_analisar, comando_gravar
from rastro.terminal import LinhaAoVivo
from tests.dubles import DADOS, HAR_DA_LOJA, PASTA_DA_LOJA, ler_relatorio


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
    monkeypatch.setattr(comando_gravar, "conferir_playwright", lambda: None)
    monkeypatch.setattr(comando_gravar, "abrir_gravacao", falsa)
    return falsa


def gravar_loja(saida: Path, *opcoes: str) -> int:
    return executar(["gravar", "https://loja.exemplo.com/", "--saida", str(saida), *opcoes])


def pastas_das_gravacoes(raiz: Path) -> list[Path]:
    return sorted((raiz / "Rastro" / "gravacoes").glob("*/*"))


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

    monkeypatch.setattr(comando_gravar, "conferir_playwright", sem_playwright)

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


def test_r24_4_navegador_que_nao_abre_encerra_com_1_e_tira_a_pasta(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.erro = NavegadorNaoAbriu("Looks like you launched a headed browser")

    assert gravar_loja(tmp_path, "--sem-ia") == 1

    assert "não foi possível abrir o navegador" in capsys.readouterr().err
    assert pastas_das_gravacoes(tmp_path) == []


def test_r24_6_usuario_e_senha_da_url_nao_vao_para_a_pasta_nem_para_o_terminal(
    capsys: pytest.CaptureFixture[str], tmp_path: Path, gravacao: GravacaoFalsa
) -> None:
    gravacao.sessao.falha_ao_ir = "net::ERR_CONNECTION_REFUSED"
    url = "https://ana:segredo@loja.exemplo.com/"

    executar(["gravar", url, "--sem-ia", "--nao-abrir", "--saida", str(tmp_path / "r")])

    [pasta] = pastas_das_gravacoes(tmp_path)
    assert pasta.parent.name == "loja.exemplo.com"
    assert gravacao.sessao.urls == [url]
    terminal = capsys.readouterr()
    assert "segredo" not in terminal.out + terminal.err


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


def test_r24_18_no_terminal_mostra_ao_vivo_o_tempo_e_as_requisicoes_gravadas(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    gravacao: GravacaoFalsa,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        comando_gravar, "LinhaAoVivo", lambda: LinhaAoVivo(sys.stdout, ao_vivo=True)
    )
    monkeypatch.setattr(
        comando_analisar, "LinhaAoVivo", lambda: LinhaAoVivo(sys.stdout, ao_vivo=True)
    )

    assert gravar_loja(tmp_path / "relatorios", "--sem-ia", "--nao-abrir") == 0

    terminal = capsys.readouterr().out
    assert "Abrindo o navegador · 0:00" in terminal
    assert "Abrindo https://loja.exemplo.com/ · 0:00" in terminal
    assert "Gravando · 0:00 · requisições 3 · scripts 1 · feche a janela para analisar" in terminal
    assert "Salvando a gravação · 0:00" in terminal


@pytest.fixture
def enter(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    lidos: list[str] = []

    def apertar_enter() -> str:
        lidos.append("")
        return ""

    monkeypatch.setattr(comando_gravar, "ler_enter", apertar_enter)
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


@pytest.mark.usefixtures("enter")
def test_r24_18_no_terminal_o_robo_mostra_ao_vivo_as_paginas_e_o_tempo(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    gravacao: GravacaoFalsa,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gravacao.sessao.urls_antes_de_fechar = 2
    monkeypatch.setattr(
        comando_gravar, "LinhaAoVivo", lambda: LinhaAoVivo(sys.stdout, ao_vivo=True)
    )
    monkeypatch.setattr(
        comando_analisar, "LinhaAoVivo", lambda: LinhaAoVivo(sys.stdout, ao_vivo=True)
    )

    assert gravar_loja(tmp_path / "relatorios", "--robo", "--sem-ia", "--nao-abrir") == 0

    terminal = capsys.readouterr().out
    assert "Robô navegando · páginas 0/20 · requisições 3 · 0:00" in terminal
    assert "páginas 1/20 · requisições 3 · scripts 1" in terminal


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

    monkeypatch.setattr(comando_gravar, "ler_enter", nunca_aperta)
    gravacao.sessao = SessaoFalsa(ctrl_c=True)
    saida = tmp_path / "relatorios"

    assert gravar_loja(saida, "--robo", "--sem-ia", "--nao-abrir") == 0

    sem_enter.set()
    assert "O robô vai navegar" not in capsys.readouterr().out
    assert gravacao.sessao.urls == ["https://loja.exemplo.com/"]
    assert (saida / PASTA_DA_LOJA / "relatorio.json").is_file()
