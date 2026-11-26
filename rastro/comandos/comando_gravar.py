import signal
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from rastro.captura.navegador_playwright import (
    NavegadorAusente,
    NavegadorNaoAbriu,
    PlaywrightAusente,
    abrir_gravacao,
    conferir_playwright,
)
from rastro.captura.pasta import (
    GravacaoJaExiste,
    UrlInvalida,
    caminho_da_gravacao,
    criar_pasta_da_gravacao,
    desfazer_pasta_da_gravacao,
    host_da_url,
    pasta_padrao_das_gravacoes,
    url_sem_usuario_e_senha,
)
from rastro.captura.robo import LIMITES_PADRAO, PassoDoRobo, ResultadoDoRobo, Robo
from rastro.captura.sessao import (
    FalhaAoNavegar,
    PedidoDeParada,
    SessaoDeGravacao,
    esperar_a_janela_fechar,
    esperar_o_enter,
)
from rastro.comandos.comando_analisar import (
    SUGESTAO_SEM_IA,
    analisar_e_gravar,
    avisar_analise_com_ia,
    avisar_analise_sem_ia,
    montar_cliente_de_ia,
)
from rastro.comandos.saida_de_erro import encerrar_com_erro
from rastro.ia.cliente import CliDaIaAusente, IaInvalida
from rastro.terminal import LinhaAoVivo, escrever_tempo

TEXTO_GRAVANDO = (
    "Gravando a visita a {host}. Navegue pelo site como um usuário comum "
    "e feche a janela quando terminar (ou aperte Ctrl+C aqui)."
)
TEXTO_FALHA_NA_PRIMEIRA_PAGINA = (
    "Não foi possível abrir {url} ({motivo}). A janela continua aberta: "
    "confira o endereço nela ou feche-a para encerrar."
)
PEDIDO_ANTES_DO_ROBO = (
    "Antes de o robô começar: se o site pede login, entre agora na janela aberta e depois "
    "aperte Enter aqui. Para o robô navegar sem login, só aperte Enter."
)
AVISO_ANTES_DO_ROBO = (
    "Cuidado em sistema de produção: o robô só segue links, mas um link comum pode "
    "disparar uma ação (aprovar, arquivar, enviar). Se o usuário tem permissão de "
    "administrador ou acesso a dados sensíveis, não entre com ele para o robô: grave sem "
    "--robo e navegue você mesmo."
)
TEXTO_JANELA_CONTINUA_ABERTA = (
    "A janela continua aberta: visite mais alguma página importante (como uma tela que fica "
    "longe da inicial) e feche a janela para analisar. Ctrl+C aqui também encerra."
)
TEXTO_ROBO_COMECOU = (
    "O robô vai navegar pelos links de {host}: até {paginas} páginas, {minutos:g} minutos "
    "e {cliques} cliques da página inicial. Ctrl+C aqui ou fechar a janela param o robô."
)
TEXTO_PASSO_DO_ROBO = (
    "  páginas {paginas}/{limite} · requisições {requisicoes} · scripts {scripts} · {tempo} · {url}"
)
TEXTO_PASSO_QUE_FALHOU = "  não abriu: {url} ({motivo})"
TEXTO_ROBO_PAROU = (
    "O robô parou: {motivo}. {paginas} páginas visitadas, {barrados} links perigosos ou "
    "de fora do site não seguidos, {parecidos} páginas parecidas demais com outras puladas."
)
TEXTO_ABRINDO_O_NAVEGADOR = "Abrindo o navegador"
TEXTO_ABRINDO_A_PAGINA = "Abrindo {url}"
TEXTO_GRAVANDO_AO_VIVO = (
    "Gravando · {tempo} · requisições {requisicoes} · scripts {scripts} · "
    "feche a janela para analisar"
)
TEXTO_ROBO_AO_VIVO = (
    "Robô navegando · páginas {paginas}/{limite} · requisições {requisicoes} · {tempo}"
)
TEXTO_SALVANDO_A_GRAVACAO = "Salvando a gravação"
TEXTO_HAR_GRAVADO = "Visita gravada em: {har}"
AVISO_SESSAO_NO_HAR = (
    "Atenção: este HAR guarda a sessão do site (cabeçalhos Cookie e Set-Cookie). "
    "Não compartilhe o arquivo; apague-o quando não precisar mais. "
    "O relatório não traz esses valores."
)
TEXTO_NADA_GRAVADO = (
    "nenhuma requisição foi gravada: a janela foi fechada antes de o site carregar. "
    "Nenhum relatório foi gerado."
)
TEXTO_HAR_PERDIDO = "o navegador fechou antes de gravar o HAR. Nenhum relatório foi gerado."


def gravar_e_analisar(
    url: str,
    saida: Path | None,
    opcao_ia: str | None,
    sem_ia: bool,
    abrir: bool,
    robo: bool = False,
) -> int:
    try:
        host = host_da_url(url)
        ia = None if sem_ia else montar_cliente_de_ia(opcao_ia)
        conferir_playwright()
        pasta = caminho_da_gravacao(pasta_padrao_das_gravacoes(), host, datetime.now())
        har = criar_pasta_da_gravacao(pasta)
    except CliDaIaAusente as erro:
        return encerrar_com_erro(f"{erro}. Escolha outra IA com --ia. {SUGESTAO_SEM_IA}")
    except (UrlInvalida, IaInvalida, PlaywrightAusente, GravacaoJaExiste) as erro:
        return encerrar_com_erro(str(erro))
    try:
        requisicoes = gravar_visita(url, host, har, robo)
    except (NavegadorAusente, NavegadorNaoAbriu) as erro:
        desfazer_pasta_da_gravacao(pasta)
        return encerrar_com_erro(str(erro))
    if requisicoes == 0:
        return encerrar_com_erro(TEXTO_NADA_GRAVADO)
    if not har.is_file():
        return encerrar_com_erro(TEXTO_HAR_PERDIDO)
    print(TEXTO_HAR_GRAVADO.format(har=har))
    print(AVISO_SESSAO_NO_HAR)
    print()
    if ia is None:
        avisar_analise_sem_ia()
    else:
        avisar_analise_com_ia(ia)
    return analisar_e_gravar(har, saida, ia, abrir, gravado_pelo_rastro=True)


def gravar_visita(url: str, host: str, har: Path, robo: bool) -> int:
    parada = PedidoDeParada()
    with LinhaAoVivo() as linha:
        linha.acompanhar(cronometrado(TEXTO_ABRINDO_O_NAVEGADOR))
        with ctrl_c_pede_parada(parada), abrir_gravacao(har) as sessao:
            if robo:
                navegar_com_o_robo(sessao, parada, url, host, linha)
            else:
                linha.pedir(TEXTO_GRAVANDO.format(host=host))
                abrir_primeira_pagina(sessao, url, linha)
                esperar_gravando(sessao, parada, linha)
            requisicoes = sessao.requisicoes
            linha.acompanhar(cronometrado(TEXTO_SALVANDO_A_GRAVACAO))
    return requisicoes


def cronometrado(texto: str) -> Callable[[], str]:
    inicio = time.monotonic()
    return lambda: f"{texto} · {escrever_tempo(time.monotonic() - inicio)}"


def esperar_gravando(sessao: SessaoDeGravacao, parada: PedidoDeParada, linha: LinhaAoVivo) -> None:
    inicio = time.monotonic()
    linha.acompanhar(
        lambda: TEXTO_GRAVANDO_AO_VIVO.format(
            tempo=escrever_tempo(time.monotonic() - inicio),
            requisicoes=sessao.requisicoes,
            scripts=sessao.scripts,
        )
    )
    esperar_a_janela_fechar(sessao, parada)


def navegar_com_o_robo(
    sessao: SessaoDeGravacao,
    parada: PedidoDeParada,
    url: str,
    host: str,
    linha: LinhaAoVivo,
) -> None:
    abrir_primeira_pagina(sessao, url, linha)
    linha.soltar()
    linha.imprimir(AVISO_ANTES_DO_ROBO)
    linha.pedir(PEDIDO_ANTES_DO_ROBO)
    if not esperar_o_enter(sessao, parada, ler_enter):
        return
    limites = LIMITES_PADRAO
    linha.imprimir(
        TEXTO_ROBO_COMECOU.format(
            host=host,
            paginas=limites.paginas,
            minutos=limites.segundos / 60,
            cliques=limites.cliques,
        )
    )
    inicio = time.monotonic()
    robo = Robo(
        sessao, parada, time.monotonic, lambda passo: mostrar_passo_do_robo(passo, linha), limites
    )
    linha.acompanhar(
        lambda: TEXTO_ROBO_AO_VIVO.format(
            paginas=robo.paginas,
            limite=limites.paginas,
            tempo=escrever_tempo(time.monotonic() - inicio),
            requisicoes=sessao.requisicoes,
        )
    )
    mostrar_fim_do_robo(robo.navegar(url), linha)
    if parada.motivo is not None:
        return
    linha.pedir(TEXTO_JANELA_CONTINUA_ABERTA)
    esperar_gravando(sessao, parada, linha)


def ler_enter() -> str:
    return input()


def mostrar_passo_do_robo(passo: PassoDoRobo, linha: LinhaAoVivo) -> None:
    if passo.falha is not None:
        linha.imprimir(
            TEXTO_PASSO_QUE_FALHOU.format(
                url=url_sem_usuario_e_senha(passo.url), motivo=passo.falha
            )
        )
        return
    linha.imprimir(
        TEXTO_PASSO_DO_ROBO.format(
            paginas=passo.paginas,
            limite=LIMITES_PADRAO.paginas,
            requisicoes=passo.requisicoes,
            scripts=passo.scripts,
            tempo=escrever_tempo(passo.segundos),
            url=url_sem_usuario_e_senha(passo.url),
        )
    )


def mostrar_fim_do_robo(resultado: ResultadoDoRobo, linha: LinhaAoVivo) -> None:
    linha.imprimir(
        TEXTO_ROBO_PAROU.format(
            motivo=resultado.motivo,
            paginas=resultado.paginas,
            barrados=resultado.barrados,
            parecidos=resultado.parecidos,
        )
    )


def abrir_primeira_pagina(sessao: SessaoDeGravacao, url: str, linha: LinhaAoVivo) -> None:
    sem_senha = url_sem_usuario_e_senha(url)
    linha.acompanhar(cronometrado(TEXTO_ABRINDO_A_PAGINA.format(url=sem_senha)))
    try:
        sessao.ir(url)
    except FalhaAoNavegar as erro:
        linha.pedir(TEXTO_FALHA_NA_PRIMEIRA_PAGINA.format(url=sem_senha, motivo=erro))


@contextmanager
def ctrl_c_pede_parada(parada: PedidoDeParada) -> Iterator[None]:
    original = signal.signal(signal.SIGINT, lambda *_: parada.pedir("Ctrl+C"))
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, original)
