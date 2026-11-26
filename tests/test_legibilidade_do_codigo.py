import ast
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PASTA_DO_CODIGO = Path(__file__).resolve().parent.parent / "rastro"
MAXIMO_DE_NIVEIS_DE_BLOCO = 2

FUNCOES = (ast.FunctionDef, ast.AsyncFunctionDef)

Corpos = list[list[ast.stmt]]


@dataclass(frozen=True)
class FuncaoAninhadaDemais:
    arquivo: str
    linha: int
    nome: str
    niveis: int

    def descrever(self) -> str:
        return f"{self.arquivo}:{self.linha} {self.nome} ({self.niveis} níveis)"


def corpo_e_senao(no: Any) -> Corpos:
    return [no.body, no.orelse]


def so_o_corpo(no: Any) -> Corpos:
    return [no.body]


def corpos_do_try(no: Any) -> Corpos:
    corpos = [no.body, no.orelse, no.finalbody]
    for tratamento in no.handlers:
        corpos.append(tratamento.body)
    return corpos


def corpos_do_match(no: Any) -> Corpos:
    corpos = []
    for caso in no.cases:
        corpos.append(caso.body)
    return corpos


CORPOS_PELO_TIPO_DE_BLOCO: dict[type[ast.AST], Callable[[Any], Corpos]] = {
    ast.If: corpo_e_senao,
    ast.For: corpo_e_senao,
    ast.AsyncFor: corpo_e_senao,
    ast.While: corpo_e_senao,
    ast.With: so_o_corpo,
    ast.AsyncWith: so_o_corpo,
    ast.Try: corpos_do_try,
    ast.Match: corpos_do_match,
}


def e_elif(no: ast.If) -> bool:
    return len(no.orelse) == 1 and isinstance(no.orelse[0], ast.If)


def niveis_do_bloco(no: ast.stmt, nivel_de_fora: int) -> int:
    if type(no) not in CORPOS_PELO_TIPO_DE_BLOCO:
        return nivel_de_fora
    nivel = nivel_de_fora + 1
    if isinstance(no, ast.If) and e_elif(no):
        niveis_do_if = niveis_dos_comandos(no.body, nivel)
        niveis_do_elif = niveis_do_bloco(no.orelse[0], nivel_de_fora)
        return max(niveis_do_if, niveis_do_elif)
    maior = nivel
    for corpo in CORPOS_PELO_TIPO_DE_BLOCO[type(no)](no):
        maior = max(maior, niveis_dos_comandos(corpo, nivel))
    return maior


def niveis_dos_comandos(comandos: list[ast.stmt], nivel_de_fora: int) -> int:
    maior = nivel_de_fora
    for comando in comandos:
        maior = max(maior, niveis_do_bloco(comando, nivel_de_fora))
    return maior


def funcoes_do_arquivo(arvore: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    funcoes: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for no in ast.walk(arvore):
        if isinstance(no, FUNCOES):
            funcoes.append(no)
    return funcoes


def funcoes_aninhadas_demais(arquivo: Path) -> list[FuncaoAninhadaDemais]:
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    nome_do_arquivo = arquivo.relative_to(PASTA_DO_CODIGO.parent).as_posix()
    encontradas: list[FuncaoAninhadaDemais] = []
    for funcao in funcoes_do_arquivo(arvore):
        niveis = niveis_dos_comandos(funcao.body, 0)
        if niveis > MAXIMO_DE_NIVEIS_DE_BLOCO:
            encontradas.append(
                FuncaoAninhadaDemais(nome_do_arquivo, funcao.lineno, funcao.name, niveis)
            )
    return encontradas


def niveis_de_uma_funcao(codigo: str) -> int:
    funcao = ast.parse(codigo).body[0]
    assert isinstance(funcao, ast.FunctionDef)
    return niveis_dos_comandos(funcao.body, 0)


def test_r19_4_nenhuma_funcao_tem_mais_de_dois_niveis_de_bloco() -> None:
    encontradas: list[FuncaoAninhadaDemais] = []
    for arquivo in sorted(PASTA_DO_CODIGO.rglob("*.py")):
        encontradas.extend(funcoes_aninhadas_demais(arquivo))

    descricoes = [funcao.descrever() for funcao in encontradas]
    assert descricoes == [], "funções com mais de dois níveis de bloco:\n" + "\n".join(descricoes)


def test_r19_4_conferencia_conta_if_dentro_de_for_dentro_de_if_como_tres_niveis() -> None:
    codigo = (
        "def f(itens, ligado):\n"
        "    if ligado:\n"
        "        for item in itens:\n"
        "            if item:\n"
        "                return item\n"
    )

    assert niveis_de_uma_funcao(codigo) == 3


def test_r19_4_conferencia_nao_soma_nivel_no_elif() -> None:
    codigo = (
        "def f(valor):\n"
        "    if valor == 1:\n"
        "        return 'um'\n"
        "    elif valor == 2:\n"
        "        return 'dois'\n"
        "    elif valor == 3:\n"
        "        return 'tres'\n"
        "    else:\n"
        "        return 'outro'\n"
    )

    assert niveis_de_uma_funcao(codigo) == 1


def test_r19_4_conferencia_conta_try_e_with_e_recomeca_na_funcao_interna() -> None:
    codigo = (
        "def f(caminho):\n"
        "    try:\n"
        "        with open(caminho) as arquivo:\n"
        "            def interna():\n"
        "                if arquivo:\n"
        "                    return 1\n"
        "            return interna()\n"
        "    except OSError:\n"
        "        return 0\n"
    )

    assert niveis_de_uma_funcao(codigo) == 2
