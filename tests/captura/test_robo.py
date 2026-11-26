from rastro.captura.espera_da_gravacao import PedidoDeParada
from rastro.captura.robo import Limites, PassoDoRobo, ResultadoDoRobo, Robo
from rastro.captura.sessao import FalhaAoNavegar

INICIO = "https://loja.exemplo.com/"


class SessaoComSiteEmMemoria:
    def __init__(
        self,
        paginas: dict[str, list[str]],
        quebradas: frozenset[str] = frozenset(),
        redirecionamentos: dict[str, str] | None = None,
    ):
        self.paginas = paginas
        self.quebradas = quebradas
        self.redirecionamentos = redirecionamentos or {}
        self.visitadas: list[str] = []
        self.atual = ""
        self.requisicoes = 0
        self.scripts = 0
        self.fechada = False
        self.ao_visitar: list[object] = []

    def abrir_pagina(self, url: str) -> None:
        if url in self.quebradas:
            raise FalhaAoNavegar("net::ERR_CONNECTION_REFUSED")
        self.visitadas.append(url)
        self.atual = self.redirecionamentos.get(url, url)
        self.requisicoes += 2
        self.scripts += 1

    def links(self) -> list[str]:
        return self.paginas.get(self.atual, [])

    def endereco(self) -> str:
        return self.atual

    def aberta(self) -> bool:
        return not self.fechada

    def esperar(self, segundos: float) -> None:
        return None


class RelogioFalso:
    def __init__(self, passo: float = 1.0) -> None:
        self.agora = 0.0
        self.passo = passo

    def __call__(self) -> float:
        self.agora += self.passo
        return self.agora


def navegar(
    site: SessaoComSiteEmMemoria,
    limites: Limites | None = None,
    parada: PedidoDeParada | None = None,
    relogio: RelogioFalso | None = None,
) -> tuple[ResultadoDoRobo, list[PassoDoRobo]]:
    passos: list[PassoDoRobo] = []
    robo = Robo(
        site,
        parada or PedidoDeParada(),
        relogio or RelogioFalso(),
        passos.append,
        limites or Limites(),
    )
    return robo.navegar(INICIO), passos


def test_r24_11_nunca_visita_a_mesma_pagina_duas_vezes() -> None:
    site = SessaoComSiteEmMemoria(
        {
            INICIO: ["/a", "/b?pagina=1"],
            f"{INICIO}a": ["/", "/b?pagina=2", "/a#topo"],
            f"{INICIO}b?pagina=1": ["/a", "/"],
        }
    )

    resultado, _ = navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}a", f"{INICIO}b?pagina=1"]
    assert resultado.motivo == "nenhum link novo a até 2 cliques da página inicial"


def test_r24_10_visita_os_links_em_ordem_alfabetica() -> None:
    site = SessaoComSiteEmMemoria({INICIO: ["/c", "/a", "/b"]})

    navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}a", f"{INICIO}b", f"{INICIO}c"]


def test_r24_12_links_barrados_nao_sao_visitados_e_sao_contados() -> None:
    site = SessaoComSiteEmMemoria({INICIO: ["/sair", "https://outro.exemplo.com/", "/produtos"]})

    resultado, _ = navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}produtos"]
    assert resultado.barrados == 2


def test_r24_13_para_no_limite_de_paginas() -> None:
    site = SessaoComSiteEmMemoria({INICIO: [f"/p{numero}" for numero in range(10)]})

    resultado, _ = navegar(site, Limites(paginas=3, por_familia=99))

    assert len(site.visitadas) == 3
    assert resultado.motivo == "limite de 3 páginas"


def test_r24_13_para_no_limite_de_tempo() -> None:
    site = SessaoComSiteEmMemoria({INICIO: [f"/p{numero}" for numero in range(10)]})

    resultado, _ = navegar(
        site, Limites(segundos=180, por_familia=99), relogio=RelogioFalso(passo=50)
    )

    assert resultado.motivo == "limite de 3 minutos"
    assert len(site.visitadas) < 10


def test_r24_13_nao_passa_de_dois_cliques_da_pagina_inicial() -> None:
    site = SessaoComSiteEmMemoria(
        {
            INICIO: ["/um"],
            f"{INICIO}um": ["/um/dois"],
            f"{INICIO}um/dois": ["/um/dois/tres"],
        }
    )

    navegar(site)

    assert f"{INICIO}um/dois/tres" not in site.visitadas
    assert f"{INICIO}um/dois" in site.visitadas


def test_r24_13_no_maximo_duas_paginas_por_familia() -> None:
    blocos = [f"/admin/blocos/{nome}" for nome in ("a", "b", "c", "d")]
    site = SessaoComSiteEmMemoria({INICIO: [*blocos, "/node/add"]})

    resultado, _ = navegar(site)

    assert site.visitadas == [
        INICIO,
        f"{INICIO}admin/blocos/a",
        f"{INICIO}admin/blocos/b",
        f"{INICIO}node/add",
    ]
    assert resultado.parecidos == 2


def test_r24_13_pagina_que_falhou_nao_gasta_a_vaga_da_familia() -> None:
    licoes = [f"#lesson/{nome}.lesson" for nome in ("a", "b", "c")]
    quebradas = frozenset({f"{INICIO}#lesson/a.lesson"})
    site = SessaoComSiteEmMemoria({INICIO: licoes}, quebradas=quebradas)

    _, passos = navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}#lesson/b.lesson", f"{INICIO}#lesson/c.lesson"]
    assert [passo.falha for passo in passos] == [None, "net::ERR_CONNECTION_REFUSED", None, None]


def test_r24_15_ctrl_c_para_o_robo_na_proxima_pagina() -> None:
    parada = PedidoDeParada()
    site = SessaoComSiteEmMemoria({INICIO: ["/a", "/b"]})
    passos: list[PassoDoRobo] = []

    def ctrl_c_depois_da_primeira(passo: PassoDoRobo) -> None:
        passos.append(passo)
        parada.pedir("Ctrl+C")

    resultado = Robo(site, parada, RelogioFalso(), ctrl_c_depois_da_primeira).navegar(INICIO)

    assert site.visitadas == [INICIO]
    assert resultado.motivo == "Ctrl+C"


def test_r24_15_janela_fechada_para_o_robo() -> None:
    site = SessaoComSiteEmMemoria({INICIO: ["/a", "/b"]})

    def fechar_a_janela(passo: PassoDoRobo) -> None:
        site.fechada = True

    resultado = Robo(site, PedidoDeParada(), RelogioFalso(), fechar_a_janela).navegar(INICIO)

    assert site.visitadas == [INICIO]
    assert resultado.motivo == "janela fechada"


def test_r24_14_cada_pagina_traz_o_progresso() -> None:
    site = SessaoComSiteEmMemoria({INICIO: ["/a"]})

    _, passos = navegar(site)

    assert passos[1] == PassoDoRobo(
        url=f"{INICIO}a",
        paginas=2,
        requisicoes=4,
        scripts=2,
        segundos=passos[1].segundos,
        falha=None,
    )
    assert passos[1].segundos > passos[0].segundos


def test_r24_13_paginas_da_raiz_nao_dividem_familia() -> None:
    site = SessaoComSiteEmMemoria({INICIO: ["/contato", "/produtos", "/sobre"]})

    resultado, _ = navegar(site)

    assert len(site.visitadas) == 4
    assert resultado.parecidos == 0


def test_r24_10_redirecionado_para_fora_nao_conta_nem_tem_links_seguidos() -> None:
    site = SessaoComSiteEmMemoria(
        {INICIO: ["/github", "/sobre"], "https://github.com/loja": ["/explore"]},
        redirecionamentos={f"{INICIO}github": "https://github.com/loja"},
    )

    resultado, passos = navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}github", f"{INICIO}sobre"]
    assert passos[1].falha == "saiu do site: foi redirecionado para github.com"
    assert resultado.paginas == 2


def test_r24_10_pagina_inicial_que_vai_para_o_www_continua_no_site() -> None:
    www = "https://www.loja.exemplo.com/"
    site = SessaoComSiteEmMemoria({www: ["/sobre"]}, redirecionamentos={INICIO: www})

    resultado, passos = navegar(site)

    assert passos[0].falha is None
    assert site.visitadas == [INICIO, f"{INICIO}sobre"]
    assert resultado.paginas == 2


def test_r24_10_porta_padrao_escrita_na_url_inicial_nao_tira_do_site() -> None:
    site = SessaoComSiteEmMemoria({"https://loja.exemplo.com/": ["/sobre"]})
    robo = Robo(site, PedidoDeParada(), RelogioFalso(), lambda _passo: None)

    resultado = robo.navegar("https://loja.exemplo.com:443/")

    assert resultado.paginas == 1
    assert site.visitadas == ["https://loja.exemplo.com:443/"]
