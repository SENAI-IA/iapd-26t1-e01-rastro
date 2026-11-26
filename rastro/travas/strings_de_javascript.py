import re

STRING_DE_JAVASCRIPT = re.compile(
    r"""
    (?P<aspa> ["'`] )
    (?P<conteudo>
        (?: \\. | (?! (?P=aspa) ) . )*?
    )
    (?P=aspa)
    """,
    re.VERBOSE | re.DOTALL,
)
ESCAPE_DE_JAVASCRIPT = re.compile(
    r"""
    \\
    (?P<sequencia>
        u \{ [0-9a-fA-F]+ \}
        | u [0-9a-fA-F]{4}
        | x [0-9a-fA-F]{2}
        | .
    )
    """,
    re.VERBOSE | re.DOTALL,
)
ESCAPES_DE_UMA_LETRA = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}
BASE_HEXADECIMAL = 16
INICIO_DO_CODIGO_ENTRE_CHAVES = "u{"
LETRAS_DO_CODIGO_HEXADECIMAL = "ux"


def strings_do_trecho(trecho: str) -> list[str]:
    valores = []
    for string in STRING_DE_JAVASCRIPT.finditer(trecho):
        valor = resolver_escapes(string.group("conteudo"))
        if valor:
            valores.append(valor)
    return valores


def resolver_escapes(conteudo: str) -> str:
    return ESCAPE_DE_JAVASCRIPT.sub(valor_do_escape_encontrado, conteudo)


def valor_do_escape_encontrado(escape: re.Match[str]) -> str:
    return valor_do_escape(escape.group("sequencia"))


def valor_do_escape(sequencia: str) -> str:
    if sequencia.startswith(INICIO_DO_CODIGO_ENTRE_CHAVES):
        return caractere_do_codigo_hexadecimal(codigo_entre_chaves(sequencia))
    if sequencia_e_codigo_hexadecimal(sequencia):
        return caractere_do_codigo_hexadecimal(codigo_depois_da_letra(sequencia))
    return ESCAPES_DE_UMA_LETRA.get(sequencia, sequencia)


def sequencia_e_codigo_hexadecimal(sequencia: str) -> bool:
    return sequencia[0] in LETRAS_DO_CODIGO_HEXADECIMAL and len(sequencia) > 1


def codigo_entre_chaves(sequencia: str) -> str:
    return sequencia.removeprefix(INICIO_DO_CODIGO_ENTRE_CHAVES).removesuffix("}")


def codigo_depois_da_letra(sequencia: str) -> str:
    return sequencia[1:]


def caractere_do_codigo_hexadecimal(codigo: str) -> str:
    return chr(int(codigo, BASE_HEXADECIMAL))


def formas_escritas(valor: str) -> list[str]:
    return [aspa + escapar(valor, aspa) + aspa for aspa in ('"', "'", "`")]


def escapar(valor: str, aspa: str) -> str:
    escapado = valor.replace("\\", "\\\\")
    escapado = escapado.replace(aspa, "\\" + aspa)
    escapado = escapado.replace("\n", "\\n")
    escapado = escapado.replace("\r", "\\r")
    return escapado.replace("\t", "\\t")
