import re
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import SplitResult, urldefrag, urljoin, urlsplit, urlunsplit

from rastro.captura.sessao import FalhaAoNavegar, PedidoDeParada, SessaoDeGravacao

PALAVRAS_PERIGOSAS = re.compile(
    r"logout|log-out|signout|sign-out|sair|delete|excluir|remove|remover|uninstall|"
    r"cron|flush|reset|token=",
    re.IGNORECASE,
)
EXTENSOES_DE_ARQUIVO = re.compile(
    r"\.(pdf|zip|gz|tar|rar|7z|exe|msi|dmg|apk|png|jpe?g|gif|svg|webp|ico|mp4|mp3|"
    r"docx?|xlsx?|pptx?|csv)$",
    re.IGNORECASE,
)
URL_DENTRO_DA_QUERY = re.compile(r"https?:|https?%3a%2f%2f|%2f%2f", re.IGNORECASE)
ESQUEMAS_NAVEGAVEIS = ("http", "https")
PORTAS_PADRAO = {"http": 80, "https": 443}
PREFIXO_WWW = "www."


@dataclass(frozen=True)
class Limites:
    paginas: int = 20
    segundos: float = 180.0
    cliques: int = 2
    por_familia: int = 2


LIMITES_PADRAO = Limites()


@dataclass(frozen=True)
class PassoDoRobo:
    url: str
    paginas: int
    requisicoes: int
    scripts: int
    segundos: float
    falha: str | None


@dataclass(frozen=True)
class ResultadoDoRobo:
    motivo: str
    paginas: int
    barrados: int
    parecidos: int


def normalizar(url: str) -> str:
    sem_fragmento, fragmento = urldefrag(url)
    partes = urlsplit(sem_fragmento)
    rota = fragmento if e_rota_de_spa(fragmento) else ""
    return urlunsplit(
        (
            partes.scheme,
            partes.netloc.lower(),
            partes.path or "/",
            chaves_da_query(partes.query),
            rota,
        )
    )


def chaves_da_query(query: str) -> str:
    chaves = [parametro.split("=", 1)[0] for parametro in query.split("&") if parametro]
    return "&".join(sorted(chaves))


def e_rota_de_spa(fragmento: str) -> bool:
    return "/" in fragmento


def familia(url: str) -> str:
    _, fragmento = urldefrag(url)
    caminho = fragmento if e_rota_de_spa(fragmento) else urlsplit(url).path
    trechos = [trecho for trecho in caminho.split("/") if trecho]
    if len(trechos) < 2:
        return "/" + "/".join(trechos)
    return "/" + "/".join(trechos[:-1])


def host_do_site(url: str) -> str:
    partes = urlsplit(url)
    host = (partes.hostname or "").removeprefix(PREFIXO_WWW)
    try:
        porta = partes.port
    except ValueError:
        return ""
    if porta is None or porta == PORTAS_PADRAO.get(partes.scheme):
        return host
    return f"{host}:{porta}"


def link_permitido(url: str, host: str) -> bool:
    partes = urlsplit(url)
    if partes.scheme not in ESQUEMAS_NAVEGAVEIS or host_do_site(url) != host:
        return False
    if tem_palavra_perigosa(partes) or leva_para_outro_endereco(partes.query):
        return False
    return not EXTENSOES_DE_ARQUIVO.search(partes.path)


def tem_palavra_perigosa(partes: SplitResult) -> bool:
    trecho_depois_do_host = f"{partes.path}?{partes.query}#{partes.fragment}"
    return PALAVRAS_PERIGOSAS.search(trecho_depois_do_host) is not None


def leva_para_outro_endereco(query: str) -> bool:
    return URL_DENTRO_DA_QUERY.search(query) is not None


def saida_do_site(endereco: str, host: str) -> str | None:
    if host_do_site(endereco) == host:
        return None
    destino = urlsplit(endereco).hostname or endereco
    return f"saiu do site: foi redirecionado para {destino}"


class Robo:
    def __init__(
        self,
        sessao: SessaoDeGravacao,
        parada: PedidoDeParada,
        relogio: Callable[[], float],
        mostrar: Callable[[PassoDoRobo], None],
        limites: Limites = LIMITES_PADRAO,
    ) -> None:
        self.sessao = sessao
        self.parada = parada
        self.relogio = relogio
        self.mostrar = mostrar
        self.limites = limites
        self.vistas: set[str] = set()
        self.por_familia: dict[str, int] = {}
        self.paginas = 0
        self.barrados = 0
        self.parecidos = 0

    def navegar(self, url_inicial: str) -> ResultadoDoRobo:
        host = host_do_site(url_inicial)
        fila: deque[tuple[str, int]] = deque([(url_inicial, 0)])
        self.vistas.add(normalizar(url_inicial))
        inicio = self.relogio()
        while fila:
            self.registrar_janela_fechada()
            motivo = self.motivo_para_parar(inicio)
            if motivo is not None:
                return self.resultado(motivo)
            url, cliques = fila.popleft()
            if self.familia_cheia(url, cliques):
                self.parecidos += 1
                continue
            if not self.visitar(url, host, inicio):
                continue
            if cliques < self.limites.cliques:
                fila.extend((link, cliques + 1) for link in self.links_novos(url, host))
        motivo = self.parada.motivo or (
            f"nenhum link novo a até {self.limites.cliques} cliques da página inicial"
        )
        return self.resultado(motivo)

    def registrar_janela_fechada(self) -> None:
        if not self.sessao.aberta():
            self.parada.pedir("janela fechada")

    def motivo_para_parar(self, inicio: float) -> str | None:
        if self.parada.motivo is not None:
            return self.parada.motivo
        if self.paginas >= self.limites.paginas:
            return f"limite de {self.limites.paginas} páginas"
        if self.relogio() - inicio >= self.limites.segundos:
            return f"limite de {self.limites.segundos / 60:g} minutos"
        return None

    def familia_cheia(self, url: str, cliques: int) -> bool:
        if cliques == 0:
            return False
        return self.por_familia.get(familia(url), 0) >= self.limites.por_familia

    def visitar(self, url: str, host: str, inicio: float) -> bool:
        falha = None
        try:
            self.sessao.ir(url)
        except FalhaAoNavegar as erro:
            falha = str(erro)
        if falha is None:
            falha = saida_do_site(self.sessao.endereco(), host)
        if falha is None:
            self.paginas += 1
            chave = familia(url)
            self.por_familia[chave] = self.por_familia.get(chave, 0) + 1
        self.mostrar(
            PassoDoRobo(
                url=url,
                paginas=self.paginas,
                requisicoes=self.sessao.requisicoes,
                scripts=self.sessao.scripts,
                segundos=self.relogio() - inicio,
                falha=falha,
            )
        )
        return falha is None

    def links_novos(self, url_da_pagina: str, host: str) -> list[str]:
        novos = []
        for href in sorted(set(self.sessao.links())):
            absoluto = urljoin(url_da_pagina, href)
            chave = normalizar(absoluto)
            if chave in self.vistas:
                continue
            self.vistas.add(chave)
            if link_permitido(absoluto, host):
                novos.append(absoluto)
            else:
                self.barrados += 1
        return novos

    def resultado(self, motivo: str) -> ResultadoDoRobo:
        return ResultadoDoRobo(motivo, self.paginas, self.barrados, self.parecidos)
