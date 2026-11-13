import argparse
import os
import sys
import webbrowser
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from rastro import atalho
from rastro.acao.plano import ROTULO_DA_PRIORIDADE
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
AJUDA_INSTALAR = "cria o comando rastro para usar em qualquer pasta"
AJUDA_DESINSTALAR = "remove o comando rastro"
TEXTO_INSTALADO = "Pronto! Comando rastro instalado."
TEXTO_TESTE_NO_MESMO_TERMINAL = "Teste com: rastro --help"
TEXTO_TESTE_NUM_TERMINAL_NOVO = "Abra um terminal novo e teste com: rastro --help"
TEXTO_DESINSTALADO = "Comando rastro removido."
TEXTO_NADA_A_REMOVER = "O comando rastro não está instalado."
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
    analisar_har.add_argument("--ia", metavar="NOME", help=AJUDA_IA)
    analisar_har.add_argument("--sem-ia", action="store_true", help=AJUDA_SEM_IA)
    analisar_har.add_argument(
        "--saida",
        type=Path,
        metavar="PASTA",
        help="pasta dos relatórios (padrão: Rastro/relatorios na pasta do usuário)",
    )
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
    if opcoes.sem_ia:
        return analisar_sem_ia(opcoes.har, opcoes.saida)
    return analisar_com_ia(opcoes.har, opcoes.saida, opcoes.ia)


def abrir_como_usar() -> int:
    caminho = caminho_do_modelo()
    with saida_do_terminal_silenciada():
        aberto = webbrowser.open(caminho.as_uri())
    if aberto:
        print(TEXTO_COMO_USAR_ABERTO.format(caminho=caminho))
    else:
        print(TEXTO_COMO_USAR_SEM_NAVEGADOR.format(caminho=caminho))
    return 0


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


def analisar_com_ia(caminho_har: Path, saida: Path | None, opcao_ia: str | None) -> int:
    try:
        ia = montar_cliente_de_ia(opcao_ia)
    except IaInvalida as erro:
        return encerrar_com_erro(str(erro))
    except CliDaIaAusente as erro:
        return encerrar_com_erro(f"{erro}. Escolha outra IA com --ia. {SUGESTAO_SEM_IA}")
    avisar_analise_com_ia(ia)
    return analisar_e_gravar(caminho_har, saida, ia)


def montar_cliente_de_ia(opcao_ia: str | None) -> ClienteDeIA:
    nome_da_ia = escolher_ia(opcao_ia, os.environ.get(VARIAVEL_DA_IA))
    executavel = localizar_cli(nome_da_ia)
    return ClienteDeIA(PROVEDORES_DAS_IAS[nome_da_ia](executavel))


def analisar_sem_ia(caminho_har: Path, saida: Path | None) -> int:
    avisar_analise_sem_ia()
    return analisar_e_gravar(caminho_har, saida, None)


def analisar_e_gravar(caminho_har: Path, saida: Path | None, ia: ClienteDeIA | None) -> int:
    try:
        analise = analisar(caminho_har, GitHubAdvisory(), RegistroNpm(), ia, Osv(), Nvd())
    except ErroAoLerHar as erro:
        return encerrar_com_erro(str(erro))
    relatorio = montar_relatorio(analise)
    aplicacao = nome_da_aplicacao(analise.site, caminho_har)
    pasta = caminho_do_relatorio(saida or pasta_padrao(), aplicacao, analise.inicio)
    try:
        gravado = gravar_relatorio(pasta, relatorio)
    except RelatorioJaExiste as erro:
        return encerrar_com_erro(str(erro))
    mostrar_resultado(pasta, gravado, relatorio)
    return 0


def avisar_analise_com_ia(ia: ClienteDeIA) -> None:
    print(AVISO_COM_IA.format(ia=ia.provedor.nome))
    print()


def avisar_analise_sem_ia() -> None:
    print(AVISO_SEM_IA)
    print(TEXTO_ACHADOS_SEM_EXPLICACAO)
    print(TEXTO_CONTINUA_IGUAL_SEM_IA)
    print()


def mostrar_resultado(pasta: Path, gravado: RelatorioGravado, relatorio: dict[str, Any]) -> None:
    print(f"Relatório gravado em: {pasta}")
    print(f"HTML: {gravado.html}")
    print(f"JSON: {gravado.json}")
    print(f"Resumo: {resumo_de_uma_linha(relatorio)}")
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
