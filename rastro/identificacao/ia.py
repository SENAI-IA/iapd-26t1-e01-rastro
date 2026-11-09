from dataclasses import dataclass
from importlib import resources

from rastro.har.modelos import Requisicao
from rastro.ia.cliente import ClienteDeIA
from rastro.ia.sanitizacao import sanitizar
from rastro.identificacao.bundles import Bundle, escolher_bundles
from rastro.identificacao.modelos import Biblioteca, Evidencia
from rastro.travas.ancoragem import conferir_ancoragem
from rastro.travas.formato import BibliotecaSugerida, conferir_formato, tirar_cerca_de_codigo
from rastro.travas.modelos import TravaAcionada

ETAPA = "identificar_bibliotecas"
ARQUIVO_DO_PROMPT = "identificar_bibliotecas.md"
MARCADOR_DA_ENTRADA = "{{entrada}}"


@dataclass(frozen=True)
class BibliotecasDaIA:
    bibliotecas: list[Biblioteca]
    travas_acionadas: list[TravaAcionada]


def identificar_em_bundles(
    requisicoes: list[Requisicao], por_assinatura: list[Biblioteca], ia: ClienteDeIA | None
) -> BibliotecasDaIA:
    if ia is None:
        return BibliotecasDaIA([], [])
    ja_identificadas = {chave(biblioteca) for biblioteca in por_assinatura}
    bibliotecas: list[Biblioteca] = []
    travas_acionadas: list[TravaAcionada] = []
    for bundle in escolher_bundles(requisicoes, por_assinatura):
        do_bundle, barrados = identificar_no_bundle(bundle, ia)
        travas_acionadas.extend(barrados)
        for biblioteca in do_bundle:
            if chave(biblioteca) not in ja_identificadas:
                ja_identificadas.add(chave(biblioteca))
                bibliotecas.append(biblioteca)
    return BibliotecasDaIA(bibliotecas, travas_acionadas)


def identificar_no_bundle(
    bundle: Bundle, ia: ClienteDeIA
) -> tuple[list[Biblioteca], list[TravaAcionada]]:
    if not bundle.trechos:
        return [], []
    trechos_enviados = [sanitizar(trecho) for trecho in bundle.trechos]
    resposta = ia.perguntar(ETAPA, montar_prompt(trechos_enviados))
    if resposta is None:
        return [], []
    sugeridas, travas_acionadas = conferir_formato(tirar_cerca_de_codigo(resposta))
    bibliotecas = []
    for sugerida in sugeridas:
        biblioteca = biblioteca_sugerida(sugerida, bundle.requisicao)
        ancorada, barrados = conferir_ancoragem(biblioteca, trechos_enviados)
        bibliotecas.append(ancorada)
        travas_acionadas.extend(barrados)
    return bibliotecas, travas_acionadas


def biblioteca_sugerida(sugerida: BibliotecaSugerida, requisicao: Requisicao) -> Biblioteca:
    evidencia = Evidencia(requisicao.indice, requisicao.url, sugerida.trecho)
    return Biblioteca(
        pacote=sugerida.pacote,
        versao=sugerida.versao,
        metodo="ia",
        situacao="confirmada",
        conferida_no_npm=None,
        travas_que_falharam=[],
        evidencias=[evidencia],
    )


def montar_prompt(trechos: list[str]) -> str:
    return ler_modelo_do_prompt().replace(MARCADOR_DA_ENTRADA, montar_entrada(trechos))


def montar_entrada(trechos: list[str]) -> str:
    blocos = [f"Trecho {numero}:\n~~~\n{trecho}\n~~~" for numero, trecho in enumerate(trechos, 1)]
    return "\n\n".join(blocos)


def ler_modelo_do_prompt() -> str:
    prompts = resources.files("rastro.ia").joinpath("prompts")
    return prompts.joinpath(ARQUIVO_DO_PROMPT).read_text(encoding="utf-8")


def chave(biblioteca: Biblioteca) -> tuple[str, str]:
    return (biblioteca.pacote, biblioteca.versao)
