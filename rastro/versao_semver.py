import re
from dataclasses import dataclass

OPERADORES = ("<=", ">=", "<", ">", "=")
PADRAO_DA_VERSAO = re.compile(
    r"""
    ^ v?
    (?P<nucleo> \d+ (?: \. \d+ ){0,2} )
    (?: - (?P<pre_lancamento> [0-9A-Za-z.-]+ ) )?
    (?: \+ [0-9A-Za-z.-]+ )?
    $
    """,
    re.VERBOSE,
)
NUMEROS_DO_NUCLEO = 3
ORDEM_DA_PARTE_NUMERICA = 0
ORDEM_DA_PARTE_DE_TEXTO = 1
ORDEM_DE_VERSAO_SEM_PRE_LANCAMENTO = 2

ParteDoPreLancamento = tuple[int, int, str]
ChaveDaVersao = tuple[tuple[int, int, int], tuple[ParteDoPreLancamento, ...]]


class FaixaIlegivel(Exception):
    pass


@dataclass(frozen=True)
class Condicao:
    operador: str
    versao: ChaveDaVersao


def versao_na_faixa(versao: str, faixa: str) -> bool:
    chave = ler_versao(versao)
    return all(condicao_atendida(chave, condicao) for condicao in ler_faixa(faixa))


def ler_faixa(faixa: str) -> list[Condicao]:
    partes = [parte.strip() for parte in faixa.split(",")]
    if alguma_condicao_vazia(partes):
        raise FaixaIlegivel("faixa vazia ou com condição vazia")
    return [ler_condicao(parte) for parte in partes]


def alguma_condicao_vazia(partes: list[str]) -> bool:
    return "" in partes


def ler_condicao(texto: str) -> Condicao:
    for operador in OPERADORES:
        if texto.startswith(operador):
            versao = texto.removeprefix(operador).strip()
            return Condicao(operador, ler_versao(versao))
    return Condicao("=", ler_versao(texto))


def ler_versao(texto: str) -> ChaveDaVersao:
    encontrado = PADRAO_DA_VERSAO.match(texto)
    if encontrado is None:
        raise FaixaIlegivel(f"versão `{texto}` fora do formato x.y.z")
    return (ler_nucleo(encontrado["nucleo"]), ler_pre_lancamento(encontrado["pre_lancamento"]))


def ler_nucleo(texto: str) -> tuple[int, int, int]:
    numeros = [int(numero) for numero in texto.split(".")]
    while len(numeros) < NUMEROS_DO_NUCLEO:
        numeros.append(0)
    return (numeros[0], numeros[1], numeros[2])


def ler_pre_lancamento(texto: str | None) -> tuple[ParteDoPreLancamento, ...]:
    if texto is None:
        return ((ORDEM_DE_VERSAO_SEM_PRE_LANCAMENTO, 0, ""),)
    return tuple(ler_parte_do_pre_lancamento(parte) for parte in texto.split("."))


def ler_parte_do_pre_lancamento(parte: str) -> ParteDoPreLancamento:
    if parte.isdigit():
        return (ORDEM_DA_PARTE_NUMERICA, int(parte), "")
    return (ORDEM_DA_PARTE_DE_TEXTO, 0, parte)


def condicao_atendida(chave: ChaveDaVersao, condicao: Condicao) -> bool:
    if condicao.operador == "<":
        return chave < condicao.versao
    if condicao.operador == "<=":
        return chave <= condicao.versao
    if condicao.operador == ">":
        return chave > condicao.versao
    if condicao.operador == ">=":
        return chave >= condicao.versao
    return chave == condicao.versao
