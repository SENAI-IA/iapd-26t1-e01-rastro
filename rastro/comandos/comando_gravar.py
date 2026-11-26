import signal
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import FrameType

from rastro.captura.endereco_da_visita import UrlInvalida, host_da_url, url_sem_usuario_e_senha
from rastro.captura.espera_da_gravacao import (
    PedidoDeParada,
    esperar_a_janela_fechar,
    esperar_o_enter,
)
from rastro.captura.navegador_playwright import (
    NavegadorAusente,
    NavegadorNaoAbriu,
    PlaywrightAusente,
    abrir_gravacao,
    conferir_playwright,
)
from rastro.captura.pasta_da_gravacao import (
    GravacaoJaExiste,
    apagar_pasta_da_gravacao,
    caminho_da_gravacao,
    criar_pasta_da_gravacao,
    pasta_padrao_das_gravacoes,
)
from rastro.captura.robo import (
    LIMITES_PADRAO,
    Limites,
    PassoDoRobo,
    ResultadoDoRobo,
    Robo,
)
from rastro.captura.sessao import FalhaAoNavegar, SessaoDeGravacao
from rastro.comandos.comando_analisar import (
    SUGESTAO_SEM_IA,
    analisar_e_gravar,
    avisar_analise_com_ia,
    avisar_analise_sem_ia,
    montar_cliente_de_ia,
)
from rastro.comandos.saida_de_erro import encerrar_com_erro
from rastro.ia.cliente import ClienteDeIA
from rastro.ia.escolha_da_ia import CLIDaIAAusente, IAInvalida
from rastro.terminal.formatacao import escrever_tempo
from rastro.terminal.linha_ao_vivo import LinhaAoVivo

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
SEGUNDOS_POR_MINUTO = 60
TEXTO_HAR_PERDIDO = "o navegador fechou antes de gravar o HAR. Nenhum relatório foi gerado."


@dataclass(frozen=True)
class GravacaoPreparada:
    host: str
    cliente_de_ia: ClienteDeIA | None
    pasta: Path
    har: Path


def gravar_e_analisar(
    url: str,
    pasta_de_saida: Path | None,
    opcao_da_ia: str | None,
    sem_ia: bool,
    abrir_no_navegador: bool,
    usar_robo: bool = False,
) -> int:
    try:
        preparada = preparar_a_gravacao(url, opcao_da_ia, sem_ia)
    except CLIDaIAAusente as erro:
        return encerrar_com_erro(f"{erro}. Escolha outra IA com --ia. {SUGESTAO_SEM_IA}")
    except (UrlInvalida, IAInvalida, PlaywrightAusente, GravacaoJaExiste) as erro:
        return encerrar_com_erro(str(erro))
    try:
        requisicoes = gravar_visita(url, preparada.host, preparada.har, usar_robo)
    except (NavegadorAusente, NavegadorNaoAbriu) as erro:
        apagar_pasta_da_gravacao(preparada.pasta)
        return encerrar_com_erro(str(erro))
    problema = problema_na_gravacao(requisicoes, preparada.har)
    if problema is not None:
        return encerrar_com_erro(problema)
    mostrar_har_gravado(preparada.har)
    avisar_a_analise(preparada.cliente_de_ia)
    return analisar_e_gravar(
        preparada.har,
        pasta_de_saida,
        preparada.cliente_de_ia,
        abrir_no_navegador,
        gravado_pelo_rastro=True,
    )


def preparar_a_gravacao(url: str, opcao_da_ia: str | None, sem_ia: bool) -> GravacaoPreparada:
    host = host_da_url(url)
    cliente_de_ia = cliente_de_ia_pedido(opcao_da_ia, sem_ia)
    conferir_playwright()
    pasta = caminho_da_gravacao(pasta_padrao_das_gravacoes(), host, datetime.now())
    har = criar_pasta_da_gravacao(pasta)
    return GravacaoPreparada(host, cliente_de_ia, pasta, har)


def cliente_de_ia_pedido(opcao_da_ia: str | None, sem_ia: bool) -> ClienteDeIA | None:
    if sem_ia:
        return None
    return montar_cliente_de_ia(opcao_da_ia)


def problema_na_gravacao(requisicoes: int, har: Path) -> str | None:
    if requisicoes == 0:
        return TEXTO_NADA_GRAVADO
    if not har.is_file():
        return TEXTO_HAR_PERDIDO
    return None


def mostrar_har_gravado(har: Path) -> None:
    print(TEXTO_HAR_GRAVADO.format(har=har))
    print(AVISO_SESSAO_NO_HAR)
    print()


def avisar_a_analise(cliente_de_ia: ClienteDeIA | None) -> None:
    if cliente_de_ia is None:
        avisar_analise_sem_ia()
    else:
        avisar_analise_com_ia(cliente_de_ia)


def gravar_visita(url: str, host: str, har: Path, usar_robo: bool) -> int:
    parada = PedidoDeParada()
    with LinhaAoVivo() as linha:
        linha.acompanhar(texto_com_tempo_decorrido(TEXTO_ABRINDO_O_NAVEGADOR))
        with parar_ao_apertar_ctrl_c(parada), abrir_gravacao(har) as sessao:
            if usar_robo:
                navegar_com_o_robo(sessao, parada, url, host, linha)
            else:
                linha.pedir(TEXTO_GRAVANDO.format(host=host))
                abrir_primeira_pagina(sessao, url, linha)
                esperar_gravando(sessao, parada, linha)
            requisicoes = sessao.requisicoes
            linha.acompanhar(texto_com_tempo_decorrido(TEXTO_SALVANDO_A_GRAVACAO))
    return requisicoes


def texto_com_tempo_decorrido(texto: str) -> Callable[[], str]:
    inicio = time.monotonic()

    def escrever_texto_com_o_tempo() -> str:
        return f"{texto} · {escrever_tempo(time.monotonic() - inicio)}"

    return escrever_texto_com_o_tempo


def esperar_gravando(sessao: SessaoDeGravacao, parada: PedidoDeParada, linha: LinhaAoVivo) -> None:
    linha.acompanhar(texto_da_gravacao_ao_vivo(sessao))
    esperar_a_janela_fechar(sessao, parada)


def texto_da_gravacao_ao_vivo(sessao: SessaoDeGravacao) -> Callable[[], str]:
    inicio = time.monotonic()

    def escrever_a_gravacao_ao_vivo() -> str:
        return TEXTO_GRAVANDO_AO_VIVO.format(
            tempo=escrever_tempo(time.monotonic() - inicio),
            requisicoes=sessao.requisicoes,
            scripts=sessao.scripts,
        )

    return escrever_a_gravacao_ao_vivo


def navegar_com_o_robo(
    sessao: SessaoDeGravacao,
    parada: PedidoDeParada,
    url: str,
    host: str,
    linha: LinhaAoVivo,
) -> None:
    abrir_primeira_pagina(sessao, url, linha)
    if not esperar_o_enter_antes_do_robo(sessao, parada, linha):
        return
    resultado = rodar_o_robo(sessao, parada, url, host, linha)
    mostrar_fim_do_robo(resultado, linha)
    if parada.motivo is not None:
        return
    linha.pedir(TEXTO_JANELA_CONTINUA_ABERTA)
    esperar_gravando(sessao, parada, linha)


def esperar_o_enter_antes_do_robo(
    sessao: SessaoDeGravacao, parada: PedidoDeParada, linha: LinhaAoVivo
) -> bool:
    linha.soltar()
    linha.imprimir(AVISO_ANTES_DO_ROBO)
    linha.pedir(PEDIDO_ANTES_DO_ROBO)
    return esperar_o_enter(sessao, parada, esperar_linha_digitada)


def rodar_o_robo(
    sessao: SessaoDeGravacao,
    parada: PedidoDeParada,
    url: str,
    host: str,
    linha: LinhaAoVivo,
) -> ResultadoDoRobo:
    limites = LIMITES_PADRAO
    avisar_o_comeco_do_robo(host, limites, linha)

    def mostrar_passo(passo: PassoDoRobo) -> None:
        mostrar_passo_do_robo(passo, linha)

    robo = Robo(sessao, parada, time.monotonic, mostrar_passo, limites)
    linha.acompanhar(texto_do_robo_ao_vivo(robo, sessao, limites))
    return robo.navegar(url)


def avisar_o_comeco_do_robo(host: str, limites: Limites, linha: LinhaAoVivo) -> None:
    linha.imprimir(
        TEXTO_ROBO_COMECOU.format(
            host=host,
            paginas=limites.paginas,
            minutos=limites.segundos / SEGUNDOS_POR_MINUTO,
            cliques=limites.cliques,
        )
    )


def texto_do_robo_ao_vivo(
    robo: Robo, sessao: SessaoDeGravacao, limites: Limites
) -> Callable[[], str]:
    inicio = time.monotonic()

    def escrever_o_robo_ao_vivo() -> str:
        return TEXTO_ROBO_AO_VIVO.format(
            paginas=robo.paginas,
            limite=limites.paginas,
            tempo=escrever_tempo(time.monotonic() - inicio),
            requisicoes=sessao.requisicoes,
        )

    return escrever_o_robo_ao_vivo


def esperar_linha_digitada() -> str:
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
    url_para_exibir = url_sem_usuario_e_senha(url)
    linha.acompanhar(texto_com_tempo_decorrido(TEXTO_ABRINDO_A_PAGINA.format(url=url_para_exibir)))
    try:
        sessao.abrir_pagina(url)
    except FalhaAoNavegar as erro:
        linha.pedir(TEXTO_FALHA_NA_PRIMEIRA_PAGINA.format(url=url_para_exibir, motivo=erro))


@contextmanager
def parar_ao_apertar_ctrl_c(parada: PedidoDeParada) -> Iterator[None]:
    def pedir_parada_pelo_ctrl_c(numero_do_sinal: int, quadro: FrameType | None) -> None:
        parada.pedir("Ctrl+C")

    original = signal.signal(signal.SIGINT, pedir_parada_pelo_ctrl_c)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, original)
