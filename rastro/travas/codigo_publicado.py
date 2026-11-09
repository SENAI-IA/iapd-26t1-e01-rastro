import re

from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.identificacao.modelos import Biblioteca, Evidencia
from rastro.travas.ancoragem import mandar_para_a_confirmar, nome_completo, versao_esta_no_trecho
from rastro.travas.modelos import TravaAcionada

TRAVA_CODIGO_CONFERE = "código confere"
MINIMO_DE_CARACTERES_ALEM_DA_VERSAO = 3
STRING_DE_JAVASCRIPT = re.compile(r"""(["'`])((?:\\.|(?!\1).)*?)\1""", re.DOTALL)
ESCAPE_DE_JAVASCRIPT = re.compile(
    r"\\(u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", re.DOTALL
)
ESCAPES_DE_UMA_LETRA = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def conferir_codigo_publicado(
    biblioteca: Biblioteca, registro: RegistroDePacotes
) -> tuple[Biblioteca, list[TravaAcionada]]:
    try:
        codigos = registro.ler_codigo(biblioteca.pacote, biblioteca.versao)
    except ConsultaNaoRealizada as erro:
        motivo = f"não foi possível ler o código publicado no npm: {erro.motivo}"
        return barrar(biblioteca, [motivo])
    motivos = [
        motivo
        for evidencia in biblioteca.evidencias
        for motivo in conferir_evidencia(biblioteca, evidencia, codigos)
    ]
    if not biblioteca.evidencias:
        motivos.append("a IA não citou trecho")
    if not motivos:
        return biblioteca, []
    return barrar(biblioteca, motivos)


def conferir_evidencia(
    biblioteca: Biblioteca, evidencia: Evidencia, codigos: list[str]
) -> list[str]:
    strings = strings_do_trecho(evidencia.trecho or "")
    if not trecho_prova_o_pacote(strings, biblioteca.versao):
        return [
            f"o trecho de {evidencia.url} não tem a versão {biblioteca.versao} "
            "e outra string que identifique o pacote"
        ]
    return [
        f"a string `{valor}` do trecho de {evidencia.url} não aparece no código publicado "
        f"de {nome_completo(biblioteca)}"
        for valor in strings
        if not string_esta_no_codigo(valor, codigos)
    ]


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


def trecho_prova_o_pacote(strings: list[str], versao: str) -> bool:
    tem_a_versao = any(versao_esta_no_trecho(versao, valor) for valor in strings)
    tem_texto_alem = any(tem_texto_alem_da_versao(valor, versao) for valor in strings)
    return tem_a_versao and tem_texto_alem


def tem_texto_alem_da_versao(valor: str, versao: str) -> bool:
    letras_e_numeros = [caractere for caractere in valor.replace(versao, "") if caractere.isalnum()]
    return len(letras_e_numeros) >= MINIMO_DE_CARACTERES_ALEM_DA_VERSAO


def string_esta_no_codigo(valor: str, codigos: list[str]) -> bool:
    formas = formas_escritas(valor)
    return any(forma in codigo for codigo in codigos for forma in formas)


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


def barrar(biblioteca: Biblioteca, motivos: list[str]) -> tuple[Biblioteca, list[TravaAcionada]]:
    alvo = nome_completo(biblioteca)
    travas_acionadas = [TravaAcionada(TRAVA_CODIGO_CONFERE, alvo, motivo) for motivo in motivos]
    return mandar_para_a_confirmar(biblioteca, travas_acionadas), travas_acionadas
