import pytest

from rastro.captura.robo import (
    Limites,
    PassoDoRobo,
    ResultadoDoRobo,
    Robo,
    familia,
    host_do_site,
    link_permitido,
    normalizar,
)
from rastro.captura.sessao import FalhaAoNavegar, PedidoDeParada

INICIO = "https://loja.exemplo.com/"
HOST = "loja.exemplo.com"


class SiteFalso:
    """Uma SessaoDeGravacao sobre um site em memória: URL -> links da página."""

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

    def ir(self, url: str) -> None:
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
    site: SiteFalso,
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


@pytest.mark.parametrize(
    ("primeira", "segunda"),
    [
        ("https://loja.exemplo.com/busca?q=a&p=1", "https://loja.exemplo.com/busca?p=2&q=b"),
        ("https://loja.exemplo.com/sobre#equipe", "https://loja.exemplo.com/sobre"),
        ("https://Loja.Exemplo.com/sobre", "https://loja.exemplo.com/sobre"),
    ],
)
def test_r24_11_mesma_pagina_com_outros_valores_ou_ancora(primeira: str, segunda: str) -> None:
    assert normalizar(primeira) == normalizar(segunda)


def test_r24_11_rota_de_spa_no_fragmento_e_outra_pagina() -> None:
    assert normalizar(f"{INICIO}#/produtos") != normalizar(f"{INICIO}#/carrinho")


@pytest.mark.parametrize(
    ("url", "esperada"),
    [
        ("https://loja.exemplo.com/admin/blocos/rodape", "/admin/blocos"),
        ("https://loja.exemplo.com/admin/blocos/rodape/", "/admin/blocos"),
        ("http://127.0.0.1:8080/WebGoat/start.mvc#lesson/CSRF.lesson", "/lesson"),
        ("https://loja.exemplo.com/contato", "/contato"),
        ("https://loja.exemplo.com/", "/"),
    ],
)
def test_r24_13_familia_e_o_caminho_sem_o_ultimo_trecho(url: str, esperada: str) -> None:
    assert familia(url) == esperada


@pytest.mark.parametrize(
    "url",
    [
        "https://outro.exemplo.com/",
        "https://loja.exemplo.com:8443/",
        "mailto:contato@loja.exemplo.com",
        "javascript:void(0)",
        "https://loja.exemplo.com/user/logout",
        "https://loja.exemplo.com/sair",
        "https://loja.exemplo.com/node/1/delete",
        "https://loja.exemplo.com/pedidos/excluir/3",
        "https://loja.exemplo.com/admin/flush?token=abc",
        "https://loja.exemplo.com/admin/run-cron",
        "https://loja.exemplo.com/catalogo.PDF",
        "https://loja.exemplo.com/fotos/vitrine.jpg",
        "https://loja.exemplo.com/redirect?to=https://github.com/loja",
        "https://loja.exemplo.com/sair-para?url=https%3A%2F%2Foutro.exemplo.com",
    ],
)
def test_r24_12_nao_segue_link_perigoso_de_fora_ou_de_arquivo(url: str) -> None:
    assert not link_permitido(url, HOST)


def test_r24_12_palavra_perigosa_no_host_nao_barra_o_site() -> None:
    assert link_permitido("https://cronos.exemplo.com/produtos", "cronos.exemplo.com")
    assert not link_permitido("https://cronos.exemplo.com/run-cron", "cronos.exemplo.com")


@pytest.mark.parametrize(
    "url",
    [
        "https://loja.exemplo.com/",
        "https://www.loja.exemplo.com/",
        "https://LOJA.exemplo.com:443/",
        "https://ana:segredo@loja.exemplo.com/",
    ],
)
def test_r24_10_mesmo_site_com_ou_sem_www_e_com_a_porta_padrao(url: str) -> None:
    assert host_do_site(url) == HOST


def test_r24_10_porta_diferente_e_outro_site() -> None:
    assert host_do_site("http://127.0.0.1:8080/") == "127.0.0.1:8080"
    assert host_do_site("https://loja.exemplo.com:8443/") != HOST


def test_r24_10_segue_link_comum_do_mesmo_site() -> None:
    assert link_permitido("https://loja.exemplo.com/produtos?pagina=2", HOST)


def test_r24_11_nunca_visita_a_mesma_pagina_duas_vezes() -> None:
    site = SiteFalso(
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
    site = SiteFalso({INICIO: ["/c", "/a", "/b"]})

    navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}a", f"{INICIO}b", f"{INICIO}c"]


def test_r24_12_links_barrados_nao_sao_visitados_e_sao_contados() -> None:
    site = SiteFalso({INICIO: ["/sair", "https://outro.exemplo.com/", "/produtos"]})

    resultado, _ = navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}produtos"]
    assert resultado.barrados == 2


def test_r24_13_para_no_limite_de_paginas() -> None:
    site = SiteFalso({INICIO: [f"/p{numero}" for numero in range(10)]})

    resultado, _ = navegar(site, Limites(paginas=3, por_familia=99))

    assert len(site.visitadas) == 3
    assert resultado.motivo == "limite de 3 páginas"


def test_r24_13_para_no_limite_de_tempo() -> None:
    site = SiteFalso({INICIO: [f"/p{numero}" for numero in range(10)]})

    resultado, _ = navegar(
        site, Limites(segundos=180, por_familia=99), relogio=RelogioFalso(passo=50)
    )

    assert resultado.motivo == "limite de 3 minutos"
    assert len(site.visitadas) < 10


def test_r24_13_nao_passa_de_dois_cliques_da_pagina_inicial() -> None:
    site = SiteFalso(
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
    site = SiteFalso({INICIO: [*blocos, "/node/add"]})

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
    site = SiteFalso({INICIO: licoes}, quebradas=quebradas)

    _, passos = navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}#lesson/b.lesson", f"{INICIO}#lesson/c.lesson"]
    assert [passo.falha for passo in passos] == [None, "net::ERR_CONNECTION_REFUSED", None, None]


def test_r24_15_ctrl_c_para_o_robo_na_proxima_pagina() -> None:
    parada = PedidoDeParada()
    site = SiteFalso({INICIO: ["/a", "/b"]})
    passos: list[PassoDoRobo] = []

    def ctrl_c_depois_da_primeira(passo: PassoDoRobo) -> None:
        passos.append(passo)
        parada.pedir("Ctrl+C")

    resultado = Robo(site, parada, RelogioFalso(), ctrl_c_depois_da_primeira).navegar(INICIO)

    assert site.visitadas == [INICIO]
    assert resultado.motivo == "Ctrl+C"


def test_r24_15_janela_fechada_para_o_robo() -> None:
    site = SiteFalso({INICIO: ["/a", "/b"]})

    def fechar_a_janela(passo: PassoDoRobo) -> None:
        site.fechada = True

    resultado = Robo(site, PedidoDeParada(), RelogioFalso(), fechar_a_janela).navegar(INICIO)

    assert site.visitadas == [INICIO]
    assert resultado.motivo == "janela fechada"


def test_r24_14_cada_pagina_traz_o_progresso() -> None:
    site = SiteFalso({INICIO: ["/a"]})

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
    site = SiteFalso({INICIO: ["/contato", "/produtos", "/sobre"]})

    resultado, _ = navegar(site)

    assert len(site.visitadas) == 4
    assert resultado.parecidos == 0


def test_r24_10_redirecionado_para_fora_nao_conta_nem_tem_links_seguidos() -> None:
    site = SiteFalso(
        {INICIO: ["/github", "/sobre"], "https://github.com/loja": ["/explore"]},
        redirecionamentos={f"{INICIO}github": "https://github.com/loja"},
    )

    resultado, passos = navegar(site)

    assert site.visitadas == [INICIO, f"{INICIO}github", f"{INICIO}sobre"]
    assert passos[1].falha == "saiu do site: foi redirecionado para github.com"
    assert resultado.paginas == 2


def test_r24_10_pagina_inicial_que_vai_para_o_www_continua_no_site() -> None:
    www = "https://www.loja.exemplo.com/"
    site = SiteFalso({www: ["/sobre"]}, redirecionamentos={INICIO: www})

    resultado, passos = navegar(site)

    assert passos[0].falha is None
    assert site.visitadas == [INICIO, f"{INICIO}sobre"]
    assert resultado.paginas == 2


def test_r24_10_porta_padrao_escrita_na_url_inicial_nao_tira_do_site() -> None:
    site = SiteFalso({"https://loja.exemplo.com/": ["/sobre"]})
    robo = Robo(site, PedidoDeParada(), RelogioFalso(), lambda _passo: None)

    resultado = robo.navegar("https://loja.exemplo.com:443/")

    assert resultado.paginas == 1
    assert site.visitadas == ["https://loja.exemplo.com:443/"]
