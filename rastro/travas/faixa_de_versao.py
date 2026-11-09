import re
from dataclasses import dataclass

from rastro.fontes.conector import Aviso
from rastro.travas.modelos import TravaAcionada

NOME_DA_TRAVA = "faixa conferida"
OPERADORES = ("<=", ">=", "<", ">", "=")
PADRAO_DA_VERSAO = re.compile(
    r"^v?(?P<nucleo>\d+(?:\.\d+){0,2})(?:-(?P<pre_lancamento>[0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)

ParteDoPreLancamento = tuple[int, int, str]
ChaveDaVersao = tuple[tuple[int, int, int], tuple[ParteDoPreLancamento, ...]]


class FaixaIlegivel(Exception):
    pass


@dataclass(frozen=True)
class Condicao:
    operador: str
    versao: ChaveDaVersao


def descartar_fora_da_faixa(
    pacote: str, versao: str, avisos: list[Aviso]
) -> tuple[list[Aviso], list[TravaAcionada]]:
    mantidos = []
    travas_acionadas = []
    for aviso in avisos:
        motivo = motivo_para_descartar(versao, aviso.versoes_afetadas)
        if motivo is None:
            mantidos.append(aviso)
        else:
            alvo = f"{aviso.ghsa} em {pacote}@{versao}"
            travas_acionadas.append(TravaAcionada(NOME_DA_TRAVA, alvo, motivo))
    return mantidos, travas_acionadas


def motivo_para_descartar(versao: str, faixa: str) -> str | None:
    try:
        if versao_na_faixa(versao, faixa):
            return None
    except FaixaIlegivel as erro:
        return f"não foi possível conferir a faixa `{faixa}`: {erro}"
    return f"a versão {versao} está fora da faixa afetada `{faixa}`"


def versao_na_faixa(versao: str, faixa: str) -> bool:
    chave = ler_versao(versao)
    return all(condicao_atendida(chave, condicao) for condicao in ler_faixa(faixa))


def ler_faixa(faixa: str) -> list[Condicao]:
    partes = [parte.strip() for parte in faixa.split(",")]
    if not all(partes):
        raise FaixaIlegivel("faixa vazia ou com condição vazia")
    return [ler_condicao(parte) for parte in partes]


def ler_condicao(texto: str) -> Condicao:
    for operador in OPERADORES:
        if texto.startswith(operador):
            return Condicao(operador, ler_versao(texto[len(operador) :].strip()))
    return Condicao("=", ler_versao(texto))


def ler_versao(texto: str) -> ChaveDaVersao:
    encontrado = PADRAO_DA_VERSAO.match(texto)
    if encontrado is None:
        raise FaixaIlegivel(f"versão `{texto}` fora do formato x.y.z")
    return (ler_nucleo(encontrado["nucleo"]), ler_pre_lancamento(encontrado["pre_lancamento"]))


def ler_nucleo(texto: str) -> tuple[int, int, int]:
    numeros = [int(numero) for numero in texto.split(".")]
    while len(numeros) < 3:
        numeros.append(0)
    return (numeros[0], numeros[1], numeros[2])


def ler_pre_lancamento(texto: str | None) -> tuple[ParteDoPreLancamento, ...]:
    if texto is None:
        return ((2, 0, ""),)
    return tuple(ler_parte_do_pre_lancamento(parte) for parte in texto.split("."))


def ler_parte_do_pre_lancamento(parte: str) -> ParteDoPreLancamento:
    if parte.isdigit():
        return (0, int(parte), "")
    return (1, 0, parte)


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
