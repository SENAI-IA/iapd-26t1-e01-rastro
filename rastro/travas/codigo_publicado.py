from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.registro_npm import RegistroDePacotes
from rastro.identificacao.modelos import Biblioteca, Evidencia, nome_com_versao
from rastro.travas.marcacao_a_confirmar import mandar_para_a_confirmar
from rastro.travas.modelos import TravaAcionada
from rastro.travas.strings_de_javascript import formas_escritas, strings_do_trecho
from rastro.travas.versao_no_trecho import versao_esta_no_trecho

TRAVA_CODIGO_CONFERE = "código confere"
MINIMO_DE_CARACTERES_ALEM_DA_VERSAO = 3


def conferir_codigo_publicado(
    biblioteca: Biblioteca, registro: RegistroDePacotes
) -> tuple[Biblioteca, list[TravaAcionada]]:
    try:
        codigos = registro.ler_codigo(biblioteca.pacote, biblioteca.versao)
    except ConsultaNaoRealizada as erro:
        motivo = f"não foi possível ler o código publicado no npm: {erro.motivo}"
        return barrar_codigo_que_nao_confere(biblioteca, [motivo])
    motivos = []
    for evidencia in biblioteca.evidencias:
        motivos.extend(conferir_evidencia_no_codigo_publicado(biblioteca, evidencia, codigos))
    if not biblioteca.evidencias:
        motivos.append("a IA não citou trecho")
    if not motivos:
        return biblioteca, []
    return barrar_codigo_que_nao_confere(biblioteca, motivos)


def conferir_evidencia_no_codigo_publicado(
    biblioteca: Biblioteca, evidencia: Evidencia, codigos: list[str]
) -> list[str]:
    strings = strings_do_trecho(evidencia.trecho or "")
    if not trecho_prova_o_pacote(strings, biblioteca.versao):
        return [
            f"o trecho de {evidencia.url} não tem a versão {biblioteca.versao} "
            "e outra string que identifique o pacote"
        ]
    motivos = []
    for valor in strings:
        if not string_esta_no_codigo(valor, codigos):
            motivos.append(
                f"a string `{valor}` do trecho de {evidencia.url} não aparece no código "
                f"publicado de {nome_com_versao(biblioteca)}"
            )
    return motivos


def trecho_prova_o_pacote(strings: list[str], versao: str) -> bool:
    tem_a_versao = any(versao_esta_no_trecho(versao, valor) for valor in strings)
    tem_texto_alem = any(tem_texto_alem_da_versao(valor, versao) for valor in strings)
    return tem_a_versao and tem_texto_alem


def tem_texto_alem_da_versao(valor: str, versao: str) -> bool:
    sem_a_versao = valor.replace(versao, "")
    letras_e_numeros = [caractere for caractere in sem_a_versao if caractere.isalnum()]
    return len(letras_e_numeros) >= MINIMO_DE_CARACTERES_ALEM_DA_VERSAO


def string_esta_no_codigo(valor: str, codigos: list[str]) -> bool:
    formas = formas_escritas(valor)
    return any(alguma_forma_no_codigo(formas, codigo) for codigo in codigos)


def alguma_forma_no_codigo(formas: list[str], codigo: str) -> bool:
    return any(forma in codigo for forma in formas)


def barrar_codigo_que_nao_confere(
    biblioteca: Biblioteca, motivos: list[str]
) -> tuple[Biblioteca, list[TravaAcionada]]:
    alvo = nome_com_versao(biblioteca)
    travas_acionadas = [TravaAcionada(TRAVA_CODIGO_CONFERE, alvo, motivo) for motivo in motivos]
    return mandar_para_a_confirmar(biblioteca, travas_acionadas), travas_acionadas
