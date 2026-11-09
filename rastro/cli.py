import argparse
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rastro.acao.plano import ROTULO_DA_PRIORIDADE
from rastro.fluxo import analisar
from rastro.fontes.github_advisory import GitHubAdvisory
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
    return leitor


def executar(argumentos: list[str] | None = None) -> int:
    leitor = criar_leitor_de_argumentos()
    opcoes = leitor.parse_args(argumentos)
    if opcoes.comando is None:
        leitor.print_help()
        return 0
    if opcoes.sem_ia:
        return analisar_sem_ia(opcoes.har, opcoes.saida)
    return analisar_com_ia(opcoes.har, opcoes.saida, opcoes.ia)


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
        analise = analisar(caminho_har, GitHubAdvisory(), RegistroNpm(), ia)
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
