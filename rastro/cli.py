import argparse
import os
import signal
import sys
import time
import webbrowser
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from rastro import atalho
from rastro.acao.plano import ROTULO_DA_PRIORIDADE
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
from rastro.captura.playwright import (
    NavegadorAusente,
    NavegadorNaoAbriu,
    PlaywrightAusente,
    abrir_gravacao,
    conferir_playwright,
)
from rastro.captura.robo import LIMITES_PADRAO, PassoDoRobo, ResultadoDoRobo, Robo
from rastro.captura.sessao import (
    FalhaAoNavegar,
    PedidoDeParada,
    SessaoDeGravacao,
    esperar_a_janela_fechar,
    esperar_o_enter,
)
from rastro.fluxo import analisar
from rastro.fontes.github_advisory import GitHubAdvisory
from rastro.fontes.nvd import Nvd
from rastro.fontes.osv import Osv
from rastro.fontes.registro_npm import RegistroNpm
from rastro.har.leitor import ErroAoLerHar
from rastro.ia.cliente import (
    IA_PADRAO,
    VARIAVEL_DA_IA,
    CliDaIaAusente,
    ClienteDeIA,
    IaInvalida,
    ProvedorDeIA,
    escolher_ia,
    localizar_cli,
)
from rastro.ia.provedores.claude import ProvedorClaude
from rastro.ia.provedores.codex import ProvedorCodex
from rastro.ia.provedores.kiro import ProvedorKiro
from rastro.relatorio.gravacao import (
    RelatorioGravado,
    RelatorioJaExiste,
    caminho_do_relatorio,
    gravar_relatorio,
    nome_da_aplicacao,
    pasta_padrao,
)
from rastro.relatorio.html import caminho_do_modelo
from rastro.relatorio.json import (
    PRIORIDADES,
    TEXTO_ACHADOS_SEM_EXPLICACAO,
    TEXTO_CONTINUA_IGUAL_SEM_IA,
    montar_relatorio,
)
from rastro.risco.nota import escrever_nota
from rastro.terminal import AndamentoNoTerminal, LinhaAoVivo, escrever_tempo

DESCRICAO = (
    "Lê um HAR, identifica as bibliotecas front-end do site e prioriza as falhas "
    "conhecidas nelas. Só análise passiva: o site analisado nunca é acessado."
)
AJUDA_SEM_IA = "analisa sem IA: não procura bibliotecas em bundles e não explica os achados"
AVISO_SEM_IA = (
    "Atenção: análise sem IA. Bibliotecas em bundles não foram procuradas; "
    "podem existir falhas que não aparecem aqui."
)
AJUDA_IA = (
    f"IA usada: kiro, claude ou codex (sem a opção, vale {VARIAVEL_DA_IA}; "
    f"sem os dois, {IA_PADRAO})"
)
SUGESTAO_SEM_IA = f"Use --sem-ia ({AJUDA_SEM_IA})."
AVISO_COM_IA = (
    "Análise com a IA {ia}. Cada chamada à IA pode levar até 2 minutos; "
    "o que ela sugere passa pelas travas antes do relatório."
)
AJUDA_COMO_USAR = "abre no navegador o guia do HAR ao relatório, sem analisar nada"
TEXTO_COMO_USAR_ABERTO = 'Guia "Como usar" aberto no navegador: {caminho}'
TEXTO_COMO_USAR_SEM_NAVEGADOR = (
    "Não foi possível abrir o navegador. Abra este arquivo nele para ver o guia "
    '"Como usar": {caminho}'
)
AJUDA_NAO_ABRIR = "não abre o relatório no navegador ao terminar"
TEXTO_RELATORIO_ABERTO = "Relatório aberto no navegador."
TEXTO_RELATORIO_SEM_NAVEGADOR = (
    "Não foi possível abrir o navegador. Abra o arquivo HTML acima nele para ver o relatório."
)
AJUDA_INSTALAR = "cria o comando rastro para usar em qualquer pasta"
AJUDA_DESINSTALAR = "remove o comando rastro"
TEXTO_INSTALADO = "Pronto! Comando rastro instalado."
TEXTO_TESTE_NO_MESMO_TERMINAL = "Teste com: rastro --help"
TEXTO_TESTE_NUM_TERMINAL_NOVO = "Abra um terminal novo e teste com: rastro --help"
TEXTO_DESINSTALADO = "Comando rastro removido."
TEXTO_NADA_A_REMOVER = "O comando rastro não está instalado."
AJUDA_GRAVAR = "abre o navegador, grava a visita num HAR e analisa ao fechar a janela"
TEXTO_GRAVANDO = (
    "Gravando a visita a {host}. Navegue pelo site como um usuário comum "
    "e feche a janela quando terminar (ou aperte Ctrl+C aqui)."
)
TEXTO_FALHA_NA_PRIMEIRA_PAGINA = (
    "Não foi possível abrir {url} ({motivo}). A janela continua aberta: "
    "confira o endereço nela ou feche-a para encerrar."
)
AJUDA_ROBO = (
    "o Rastro navega sozinho pelos links do site (só links, nunca botões nem formulários), "
    "com limite de páginas, tempo e cliques"
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
PROVEDORES_DAS_IAS: dict[str, Callable[[str], ProvedorDeIA]] = {
    "kiro": ProvedorKiro,
    "claude": ProvedorClaude,
    "codex": ProvedorCodex,
}


def criar_leitor_de_argumentos() -> argparse.ArgumentParser:
    leitor = argparse.ArgumentParser(prog="rastro", description=DESCRICAO)
    comandos = leitor.add_subparsers(dest="comando", metavar="comando")
    analisar_har = comandos.add_parser(
        "analisar",
        help="analisa um HAR e grava o relatório numa pasta nova",
        description="Analisa um HAR e grava o relatório numa pasta nova.",
    )
    analisar_har.add_argument("har", type=Path, help="arquivo HAR exportado do navegador")
    adicionar_opcoes_da_analise(analisar_har)
    gravar = comandos.add_parser(
        "gravar",
        help=AJUDA_GRAVAR,
        description=(
            "Abre o Chrome (ou o Edge) da máquina na URL, grava num HAR tudo o que o "
            "navegador receber e analisa ao fechar a janela. Precisa do Playwright."
        ),
    )
    gravar.add_argument("url", help="endereço do site, com http:// ou https://")
    gravar.add_argument("--robo", action="store_true", help=AJUDA_ROBO)
    adicionar_opcoes_da_analise(gravar)
    comandos.add_parser(
        "como-usar",
        help=AJUDA_COMO_USAR,
        description='Abre no navegador o guia "Como usar" do relatório, sem analisar nada.',
    )
    comandos.add_parser(
        "instalar",
        help=AJUDA_INSTALAR,
        description="Cria o comando rastro para usar em qualquer pasta.",
    )
    comandos.add_parser(
        "desinstalar",
        help=AJUDA_DESINSTALAR,
        description="Remove o comando rastro. O projeto e os relatórios ficam.",
    )
    return leitor


def adicionar_opcoes_da_analise(comando: argparse.ArgumentParser) -> None:
    comando.add_argument("--ia", metavar="NOME", help=AJUDA_IA)
    comando.add_argument("--sem-ia", action="store_true", help=AJUDA_SEM_IA)
    comando.add_argument(
        "--saida",
        type=Path,
        metavar="PASTA",
        help="pasta dos relatórios (padrão: Rastro/relatorios na pasta do usuário)",
    )
    comando.add_argument("--nao-abrir", action="store_true", help=AJUDA_NAO_ABRIR)


def principal() -> None:
    sys.exit(executar())


def executar(argumentos: list[str] | None = None) -> int:
    leitor = criar_leitor_de_argumentos()
    opcoes = leitor.parse_args(argumentos)
    if opcoes.comando is None:
        leitor.print_help()
        return 0
    if opcoes.comando == "como-usar":
        return abrir_como_usar()
    if opcoes.comando == "instalar":
        return instalar_comando()
    if opcoes.comando == "desinstalar":
        return desinstalar_comando()
    abrir = not opcoes.nao_abrir
    if opcoes.comando == "gravar":
        return gravar_e_analisar(
            opcoes.url, opcoes.saida, opcoes.ia, opcoes.sem_ia, abrir, opcoes.robo
        )
    if opcoes.sem_ia:
        return analisar_sem_ia(opcoes.har, opcoes.saida, abrir)
    return analisar_com_ia(opcoes.har, opcoes.saida, opcoes.ia, abrir)


def abrir_como_usar() -> int:
    caminho = caminho_do_modelo()
    if abrir_no_navegador(caminho):
        print(TEXTO_COMO_USAR_ABERTO.format(caminho=caminho))
    else:
        print(TEXTO_COMO_USAR_SEM_NAVEGADOR.format(caminho=caminho))
    return 0


def abrir_no_navegador(caminho: Path) -> bool:
    with saida_do_terminal_silenciada():
        return webbrowser.open(caminho.resolve().as_uri())


@contextmanager
def saida_do_terminal_silenciada() -> Iterator[None]:
    """Manda para o nada o que o navegador escreve no terminal.

    O navegador herda o terminal de quem o abre e, já aberto, escreve avisos
    como "Abrindo em uma sessão de navegador existente." e erros internos do Chrome.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    originais = [(descritor, os.dup(descritor)) for descritor in (1, 2)]
    nada = os.open(os.devnull, os.O_WRONLY)
    try:
        for descritor, _ in originais:
            os.dup2(nada, descritor)
        yield
    finally:
        for descritor, original in originais:
            os.dup2(original, descritor)
            os.close(original)
        os.close(nada)


def instalar_comando() -> int:
    try:
        instalacao = atalho.instalar()
    except (atalho.ProjetoNaoEncontrado, atalho.AtalhoDeOutro) as erro:
        return encerrar_com_erro(str(erro))
    print(TEXTO_INSTALADO)
    if instalacao.path_alterado_em:
        print(TEXTO_TESTE_NUM_TERMINAL_NOVO)
    else:
        print(TEXTO_TESTE_NO_MESMO_TERMINAL)
    return 0


def desinstalar_comando() -> int:
    try:
        desinstalacao = atalho.desinstalar()
    except atalho.AtalhoDeOutro as erro:
        return encerrar_com_erro(str(erro))
    if desinstalacao.atalho_removido is None and not desinstalacao.path_removido_de:
        print(TEXTO_NADA_A_REMOVER)
    else:
        print(TEXTO_DESINSTALADO)
    return 0


def analisar_com_ia(
    caminho_har: Path, saida: Path | None, opcao_ia: str | None, abrir: bool
) -> int:
    try:
        ia = montar_cliente_de_ia(opcao_ia)
    except IaInvalida as erro:
        return encerrar_com_erro(str(erro))
    except CliDaIaAusente as erro:
        return encerrar_com_erro(f"{erro}. Escolha outra IA com --ia. {SUGESTAO_SEM_IA}")
    avisar_analise_com_ia(ia)
    return analisar_e_gravar(caminho_har, saida, ia, abrir)


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


def montar_cliente_de_ia(opcao_ia: str | None) -> ClienteDeIA:
    nome_da_ia = escolher_ia(opcao_ia, os.environ.get(VARIAVEL_DA_IA))
    executavel = localizar_cli(nome_da_ia)
    return ClienteDeIA(PROVEDORES_DAS_IAS[nome_da_ia](executavel))


def analisar_sem_ia(caminho_har: Path, saida: Path | None, abrir: bool) -> int:
    avisar_analise_sem_ia()
    return analisar_e_gravar(caminho_har, saida, None, abrir)


def analisar_e_gravar(
    caminho_har: Path,
    saida: Path | None,
    ia: ClienteDeIA | None,
    abrir: bool,
    gravado_pelo_rastro: bool = False,
) -> int:
    try:
        with LinhaAoVivo() as linha:
            andamento = AndamentoNoTerminal(linha)
            analise = analisar(
                caminho_har,
                GitHubAdvisory(),
                RegistroNpm(),
                ia,
                Osv(),
                Nvd(),
                gravado_pelo_rastro=gravado_pelo_rastro,
                andamento=andamento,
            )
            andamento.terminar()
    except ErroAoLerHar as erro:
        return encerrar_com_erro(str(erro))
    relatorio = montar_relatorio(analise)
    aplicacao = nome_da_aplicacao(analise.site, caminho_har)
    pasta = caminho_do_relatorio(saida or pasta_padrao(), aplicacao, analise.inicio)
    try:
        gravado = gravar_relatorio(pasta, relatorio)
    except RelatorioJaExiste as erro:
        return encerrar_com_erro(str(erro))
    mostrar_resultado(pasta, gravado, relatorio, abrir)
    return 0


def abrir_relatorio(html: Path) -> None:
    if abrir_no_navegador(html):
        print(TEXTO_RELATORIO_ABERTO)
    else:
        print(TEXTO_RELATORIO_SEM_NAVEGADOR)


def avisar_analise_com_ia(ia: ClienteDeIA) -> None:
    print(AVISO_COM_IA.format(ia=ia.provedor.nome))
    print()


def avisar_analise_sem_ia() -> None:
    print(AVISO_SEM_IA)
    print(TEXTO_ACHADOS_SEM_EXPLICACAO)
    print(TEXTO_CONTINUA_IGUAL_SEM_IA)
    print()


def mostrar_resultado(
    pasta: Path, gravado: RelatorioGravado, relatorio: dict[str, Any], abrir: bool
) -> None:
    print(f"Relatório gravado em: {pasta}")
    print(f"HTML: {gravado.html}")
    print(f"JSON: {gravado.json}")
    print(f"Resumo: {resumo_de_uma_linha(relatorio)}")
    if abrir:
        abrir_relatorio(gravado.html)
    if relatorio["analise"]["ia"] is None:
        print(AVISO_SEM_IA)
    for texto in falhas_da_ia(relatorio):
        print(f"Atenção: {texto}")


def falhas_da_ia(relatorio: dict[str, Any]) -> list[str]:
    limitacoes = relatorio["analise"]["limitacoes"]
    return [item["texto"] for item in limitacoes if item["id"].startswith("ia_falhou_")]


def resumo_de_uma_linha(relatorio: dict[str, Any]) -> str:
    resumo = relatorio["resumo"]
    site = relatorio["analise"]["site"] or relatorio["analise"]["har"]
    partes = [
        site,
        f"bibliotecas: {resumo['bibliotecas']} ({resumo['bibliotecas_vulneraveis']} com falhas)",
        f"achados: {resumo['achados']}",
        f"nota máxima: {escrever_nota_maxima(resumo['nota_maxima'])}",
        f"ações: {resumo['acoes']} ({escrever_acoes_por_prioridade(resumo)})",
    ]
    return " · ".join(partes)


def escrever_nota_maxima(nota: float | None) -> str:
    if nota is None:
        return "sem nota"
    return escrever_nota(nota)


def escrever_acoes_por_prioridade(resumo: dict[str, Any]) -> str:
    contagem = resumo["acoes_por_prioridade"]
    return ", ".join(f"{contagem[p]} {ROTULO_DA_PRIORIDADE[p]}" for p in PRIORIDADES)


def encerrar_com_erro(mensagem: str) -> int:
    print(f"rastro: erro: {mensagem}", file=sys.stderr)
    return 1
