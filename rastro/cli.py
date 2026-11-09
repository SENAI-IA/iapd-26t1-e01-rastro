import argparse
import sys
from pathlib import Path
from typing import Any

from rastro.acao.plano import ROTULO_DA_PRIORIDADE
from rastro.fluxo import analisar
from rastro.fontes.github_advisory import GitHubAdvisory
from rastro.fontes.registro_npm import RegistroNpm
from rastro.har.leitor import ErroAoLerHar
from rastro.relatorio.gravacao import (
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
MENSAGEM_IA_INDISPONIVEL = (
    "a análise com IA ainda não está disponível nesta versão. "
    f"Use --sem-ia ({AJUDA_SEM_IA})."
)


def criar_leitor_de_argumentos() -> argparse.ArgumentParser:
    leitor = argparse.ArgumentParser(prog="rastro", description=DESCRICAO)
    comandos = leitor.add_subparsers(dest="comando", metavar="comando")
    analisar_har = comandos.add_parser(
        "analisar",
        help="analisa um HAR e grava o relatório numa pasta nova",
        description="Analisa um HAR e grava o relatório numa pasta nova.",
    )
    analisar_har.add_argument("har", type=Path, help="arquivo HAR exportado do navegador")
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
    return executar_analise(opcoes.har, opcoes.sem_ia, opcoes.saida)


def executar_analise(caminho_har: Path, sem_ia: bool, saida: Path | None) -> int:
    if not sem_ia:
        return encerrar_com_erro(MENSAGEM_IA_INDISPONIVEL)
    avisar_analise_sem_ia()
    try:
        analise = analisar(caminho_har, GitHubAdvisory(), RegistroNpm())
    except ErroAoLerHar as erro:
        return encerrar_com_erro(str(erro))
    relatorio = montar_relatorio(analise)
    aplicacao = nome_da_aplicacao(analise.site, caminho_har)
    pasta = caminho_do_relatorio(saida or pasta_padrao(), aplicacao, analise.inicio)
    try:
        caminho_do_json = gravar_relatorio(pasta, relatorio)
    except RelatorioJaExiste as erro:
        return encerrar_com_erro(str(erro))
    mostrar_resultado(pasta, caminho_do_json, relatorio)
    return 0


def avisar_analise_sem_ia() -> None:
    print(AVISO_SEM_IA)
    print(TEXTO_ACHADOS_SEM_EXPLICACAO)
    print(TEXTO_CONTINUA_IGUAL_SEM_IA)
    print()


def mostrar_resultado(pasta: Path, caminho_do_json: Path, relatorio: dict[str, Any]) -> None:
    print(f"Relatório gravado em: {pasta}")
    print(f"JSON: {caminho_do_json}")
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
