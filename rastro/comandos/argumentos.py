import argparse
from pathlib import Path
from typing import TypeAlias

from rastro.ia.cliente import IA_PADRAO, VARIAVEL_DA_IA

DESCRICAO = (
    "Lê um HAR, identifica as bibliotecas front-end do site e prioriza as falhas "
    "conhecidas nelas. A análise é passiva; o pentest ativo só roda com comando e "
    "autorização explícitos."
)
AJUDA_SEM_IA = "analisa sem IA: não procura bibliotecas em bundles e não explica os achados"
AJUDA_IA = (
    f"IA usada: kiro, claude ou codex (sem a opção, vale {VARIAVEL_DA_IA}; "
    f"sem os dois, {IA_PADRAO})"
)
AJUDA_COMO_USAR = "abre no navegador o guia do HAR ao relatório, sem analisar nada"
AJUDA_NAO_ABRIR = "não abre o relatório no navegador ao terminar"
AJUDA_INSTALAR = "cria o comando rastro para usar em qualquer pasta"
AJUDA_DESINSTALAR = "remove o comando rastro"
AJUDA_GRAVAR = "abre o navegador, grava a visita num HAR e analisa ao fechar a janela"
AJUDA_ROBO = (
    "o Rastro navega sozinho pelos links do site (só links, nunca botões nem formulários), "
    "com limite de páginas, tempo e cliques"
)
AJUDA_PENTEST = (
    "leva para a aba Segurança ativa o resultado gerado por `rastro pentest` para este mesmo HAR; "
    "não muda a nota nem o plano"
)
AJUDA_PENTEST_COMANDO = (
    "executa validações HTTP seguras no host do HAR; envia requisições somente com --autorizo"
)

ListaDeComandos: TypeAlias = "argparse._SubParsersAction[argparse.ArgumentParser]"


def criar_leitor_de_argumentos() -> argparse.ArgumentParser:
    leitor = argparse.ArgumentParser(prog="rastro", description=DESCRICAO)
    comandos = leitor.add_subparsers(dest="comando", metavar="comando")
    adicionar_comando_analisar(comandos)
    adicionar_comando_gravar(comandos)
    adicionar_comando_pentest(comandos)
    adicionar_comando_como_usar(comandos)
    adicionar_comando_instalar(comandos)
    adicionar_comando_desinstalar(comandos)
    return leitor


def adicionar_comando_analisar(comandos: ListaDeComandos) -> None:
    analisar_har = comandos.add_parser(
        "analisar",
        help="analisa um HAR e grava o relatório numa pasta nova",
        description="Analisa um HAR e grava o relatório numa pasta nova.",
    )
    analisar_har.add_argument("har", type=Path, help="arquivo HAR exportado do navegador")
    adicionar_opcoes_da_analise(analisar_har, pentest=True)


def adicionar_comando_gravar(comandos: ListaDeComandos) -> None:
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


def adicionar_comando_pentest(comandos: ListaDeComandos) -> None:
    pentest = comandos.add_parser(
        "pentest",
        help=AJUDA_PENTEST_COMANDO,
        description=(
            "Executa validações HTTP seguras no host do HAR e grava o pentest.json. "
            "O comando é opt-in: sem --autorizo nenhuma requisição é enviada."
        ),
    )
    pentest.add_argument("har", type=Path, help="arquivo HAR exportado do navegador")
    pentest.add_argument(
        "--autorizo",
        action="store_true",
        help="confirma que você tem autorização para enviar requisições ao site",
    )
    pentest.add_argument(
        "--saida",
        type=Path,
        metavar="PASTA",
        help="pasta dos pentests (padrão: Rastro/pentest na pasta do usuário)",
    )


def adicionar_comando_como_usar(comandos: ListaDeComandos) -> None:
    comandos.add_parser(
        "como-usar",
        help=AJUDA_COMO_USAR,
        description='Abre no navegador o guia "Como usar" do relatório, sem analisar nada.',
    )


def adicionar_comando_instalar(comandos: ListaDeComandos) -> None:
    comandos.add_parser(
        "instalar",
        help=AJUDA_INSTALAR,
        description="Cria o comando rastro para usar em qualquer pasta.",
    )


def adicionar_comando_desinstalar(comandos: ListaDeComandos) -> None:
    comandos.add_parser(
        "desinstalar",
        help=AJUDA_DESINSTALAR,
        description="Remove o comando rastro. O projeto e os relatórios ficam.",
    )


def adicionar_opcoes_da_analise(comando: argparse.ArgumentParser, pentest: bool = False) -> None:
    comando.add_argument("--ia", metavar="NOME", help=AJUDA_IA)
    comando.add_argument("--sem-ia", action="store_true", help=AJUDA_SEM_IA)
    comando.add_argument(
        "--saida",
        type=Path,
        metavar="PASTA",
        help="pasta dos relatórios (padrão: Rastro/relatorios na pasta do usuário)",
    )
    comando.add_argument("--nao-abrir", action="store_true", help=AJUDA_NAO_ABRIR)
    if pentest:
        comando.add_argument("--pentest", type=Path, metavar="ARQUIVO", help=AJUDA_PENTEST)
