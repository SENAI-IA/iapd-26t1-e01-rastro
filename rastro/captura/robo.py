from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin

from rastro.captura.espera_da_gravacao import PedidoDeParada
from rastro.captura.regras_dos_links import (
    familia_da_pagina,
    host_do_site,
    link_permitido,
    saida_do_site,
    url_para_comparar,
)
from rastro.captura.sessao import FalhaAoNavegar, SessaoDeGravacao

SEGUNDOS_POR_MINUTO = 60


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


@dataclass(frozen=True)
class LinkNaFila:
    url: str
    cliques: int


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
        self.urls_ja_vistas: set[str] = set()
        self.por_familia: dict[str, int] = {}
        self.paginas = 0
        self.barrados = 0
        self.parecidos = 0

    def navegar(self, url_inicial: str) -> ResultadoDoRobo:
        host = host_do_site(url_inicial)
        fila: deque[LinkNaFila] = deque([LinkNaFila(url_inicial, 0)])
        self.urls_ja_vistas.add(url_para_comparar(url_inicial))
        inicio = self.relogio()
        while fila:
            self.registrar_janela_fechada()
            motivo = self.motivo_para_parar(inicio)
            if motivo is not None:
                return self.resultado(motivo)
            self.seguir_link(fila.popleft(), fila, host, inicio)
        return self.resultado(self.motivo_do_fim_da_fila())

    def seguir_link(
        self, link: LinkNaFila, fila: deque[LinkNaFila], host: str, inicio: float
    ) -> None:
        if self.familia_cheia(link):
            self.parecidos += 1
            return
        if not self.visitar(link.url, host, inicio):
            return
        if link.cliques < self.limites.cliques:
            fila.extend(self.proximos_da_fila(link, host))

    def motivo_do_fim_da_fila(self) -> str:
        if self.parada.motivo:
            return self.parada.motivo
        return f"nenhum link novo a até {self.limites.cliques} cliques da página inicial"

    def registrar_janela_fechada(self) -> None:
        if not self.sessao.aberta():
            self.parada.pedir("janela fechada")

    def motivo_para_parar(self, inicio: float) -> str | None:
        if self.parada.motivo is not None:
            return self.parada.motivo
        if self.paginas >= self.limites.paginas:
            return f"limite de {self.limites.paginas} páginas"
        if self.relogio() - inicio >= self.limites.segundos:
            return f"limite de {self.limites.segundos / SEGUNDOS_POR_MINUTO:g} minutos"
        return None

    def familia_cheia(self, link: LinkNaFila) -> bool:
        if link.cliques == 0:
            return False
        return self.por_familia.get(familia_da_pagina(link.url), 0) >= self.limites.por_familia

    def visitar(self, url: str, host: str, inicio: float) -> bool:
        falha = self.descobrir_falha_da_visita(url, host)
        if falha is None:
            self.registrar_pagina_visitada(url)
        self.mostrar(self.passo_da_visita(url, inicio, falha))
        return falha is None

    def descobrir_falha_da_visita(self, url: str, host: str) -> str | None:
        try:
            self.sessao.abrir_pagina(url)
        except FalhaAoNavegar as erro:
            return str(erro)
        return saida_do_site(self.sessao.endereco(), host)

    def registrar_pagina_visitada(self, url: str) -> None:
        self.paginas += 1
        familia = familia_da_pagina(url)
        self.por_familia[familia] = self.por_familia.get(familia, 0) + 1

    def passo_da_visita(self, url: str, inicio: float, falha: str | None) -> PassoDoRobo:
        return PassoDoRobo(
            url=url,
            paginas=self.paginas,
            requisicoes=self.sessao.requisicoes,
            scripts=self.sessao.scripts,
            segundos=self.relogio() - inicio,
            falha=falha,
        )

    def proximos_da_fila(self, link: LinkNaFila, host: str) -> list[LinkNaFila]:
        return [LinkNaFila(novo, link.cliques + 1) for novo in self.links_novos(link.url, host)]

    def links_novos(self, url_da_pagina: str, host: str) -> list[str]:
        novos = []
        for href in sorted(set(self.sessao.links())):
            novo = self.link_novo_e_permitido(url_da_pagina, href, host)
            if novo is not None:
                novos.append(novo)
        return novos

    def link_novo_e_permitido(self, url_da_pagina: str, href: str, host: str) -> str | None:
        absoluto = urljoin(url_da_pagina, href)
        chave = url_para_comparar(absoluto)
        if chave in self.urls_ja_vistas:
            return None
        self.urls_ja_vistas.add(chave)
        if not link_permitido(absoluto, host):
            self.barrados += 1
            return None
        return absoluto

    def resultado(self, motivo: str) -> ResultadoDoRobo:
        return ResultadoDoRobo(motivo, self.paginas, self.barrados, self.parecidos)
