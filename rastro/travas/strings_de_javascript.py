import re

STRING_DE_JAVASCRIPT = re.compile(r"""(["'`])((?:\\.|(?!\1).)*?)\1""", re.DOTALL)
ESCAPE_DE_JAVASCRIPT = re.compile(
    r"\\(u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", re.DOTALL
)
ESCAPES_DE_UMA_LETRA = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def strings_do_trecho(trecho: str) -> list[str]:
    valores = [resolver_escapes(conteudo) for _, conteudo in STRING_DE_JAVASCRIPT.findall(trecho)]
    return [valor for valor in valores if valor]


def resolver_escapes(conteudo: str) -> str:
    return ESCAPE_DE_JAVASCRIPT.sub(lambda escape: valor_do_escape(escape.group(1)), conteudo)


def valor_do_escape(sequencia: str) -> str:
    if sequencia.startswith("u{"):
        return chr(int(sequencia[2:-1], 16))
    if sequencia[0] in "ux" and len(sequencia) > 1:
        return chr(int(sequencia[1:], 16))
    return ESCAPES_DE_UMA_LETRA.get(sequencia, sequencia)


def formas_escritas(valor: str) -> list[str]:
    return [aspa + escapar(valor, aspa) + aspa for aspa in ('"', "'", "`")]


def escapar(valor: str, aspa: str) -> str:
    return (
        valor.replace("\\", "\\\\")
        .replace(aspa, f"\\{aspa}")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
