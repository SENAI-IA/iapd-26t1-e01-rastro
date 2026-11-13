import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from rastro.captura.sessao import FalhaAoNavegar, SessaoDeGravacao

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Playwright, Response

VERSAO_DO_PLAYWRIGHT = "1.65.1"
CANAIS_DO_NAVEGADOR = ("chrome", "msedge")
TEMPO_LIMITE_DA_PAGINA_EM_MS = 15_000
TEXTO_DE_NAVEGADOR_NAO_ENCONTRADO = "is not found at"
LER_OS_LINKS = "elementos => elementos.map(elemento => elemento.href)"


class PlaywrightAusente(Exception):
    def __init__(self) -> None:
        super().__init__(
            "o Playwright não está instalado no Python que roda o Rastro. "
            "Para gravar a visita, instale com:\n"
            f'  "{sys.executable}" -m pip install playwright=={VERSAO_DO_PLAYWRIGHT}\n'
            "e rode de novo. O resto do Rastro funciona sem ele."
        )


class NavegadorAusente(Exception):
    def __init__(self) -> None:
        super().__init__(
            "nem o Google Chrome nem o Microsoft Edge foram encontrados nesta máquina. "
            "Instale um dos dois e rode de novo. O Rastro não baixa navegador."
        )


def conferir_playwright() -> None:
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError as erro:
        raise PlaywrightAusente() from erro


class SessaoPlaywright:
    def __init__(self, contexto: "BrowserContext") -> None:
        self._contexto = contexto
        self._pagina = contexto.new_page()
        self.requisicoes = 0
        self.scripts = 0
        contexto.on("response", self._contar)

    def _contar(self, resposta: "Response") -> None:
        self.requisicoes += 1
        if "javascript" in (resposta.headers.get("content-type") or ""):
            self.scripts += 1

    def ir(self, url: str) -> None:
        from playwright.sync_api import Error

        try:
            self._pagina.goto(url, wait_until="networkidle", timeout=TEMPO_LIMITE_DA_PAGINA_EM_MS)
        except Error as erro:
            raise FalhaAoNavegar(str(erro).splitlines()[0]) from erro

    def links(self) -> list[str]:
        from playwright.sync_api import Error

        try:
            hrefs: list[str] = self._pagina.eval_on_selector_all("a[href]", LER_OS_LINKS)
        except Error:
            return []
        return hrefs

    def endereco(self) -> str:
        return self._pagina.url

    def aberta(self) -> bool:
        return len(self._contexto.pages) > 0

    def esperar(self, segundos: float) -> None:
        from playwright.sync_api import Error

        paginas = self._contexto.pages
        if not paginas:
            return
        try:
            paginas[0].wait_for_timeout(segundos * 1000)
        except Error:
            return


@contextmanager
def abrir_gravacao(har: Path) -> Iterator[SessaoDeGravacao]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        navegador = abrir_navegador_da_maquina(playwright)
        contexto = navegador.new_context(
            record_har_path=str(har), record_har_mode="minimal", no_viewport=True
        )
        try:
            yield SessaoPlaywright(contexto)
        finally:
            fechar(contexto, navegador)


def abrir_navegador_da_maquina(playwright: "Playwright") -> "Browser":
    from playwright.sync_api import Error

    for canal in CANAIS_DO_NAVEGADOR:
        try:
            return playwright.chromium.launch(channel=canal, headless=False, handle_sigint=False)
        except Error as erro:
            if TEXTO_DE_NAVEGADOR_NAO_ENCONTRADO not in str(erro):
                raise
    raise NavegadorAusente()


def fechar(contexto: "BrowserContext", navegador: "Browser") -> None:
    from playwright.sync_api import Error

    for fechamento in (contexto.close, navegador.close):
        try:
            fechamento()
        except Error:
            continue
