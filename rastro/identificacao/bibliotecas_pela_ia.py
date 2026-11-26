from dataclasses import dataclass

from rastro.andamento import SEM_ANDAMENTO, Andamento
from rastro.har.modelos import Requisicao
from rastro.ia.cliente import ClienteDeIA
from rastro.ia.montagem_do_prompt import montar_prompt
from rastro.ia.sanitizacao import sanitizar
from rastro.identificacao.modelos import Biblioteca, Evidencia, nome_com_versao
from rastro.identificacao.trechos_dos_bundles import Bundle, escolher_bundles
from rastro.travas.ancoragem import conferir_ancoragem
from rastro.travas.formato_das_bibliotecas import BibliotecaSugerida, conferir_formato
from rastro.travas.json_estrito import tirar_cerca_de_codigo
from rastro.travas.modelos import TravaAcionada

ETAPA = "identificar_bibliotecas"
ARQUIVO_DO_PROMPT = "identificar_bibliotecas.md"


@dataclass(frozen=True)
class BibliotecasDaIA:
    bibliotecas: list[Biblioteca]
    travas_acionadas: list[TravaAcionada]


def identificar_em_bundles(
    requisicoes: list[Requisicao],
    por_assinatura: list[Biblioteca],
    ia: ClienteDeIA | None,
    andamento: Andamento = SEM_ANDAMENTO,
) -> BibliotecasDaIA:
    if ia is None:
        return BibliotecasDaIA([], [])
    ja_identificadas = {nome_com_versao(biblioteca) for biblioteca in por_assinatura}
    da_ia: dict[str, Biblioteca] = {}
    travas_acionadas: list[TravaAcionada] = []
    bundles = escolher_bundles(requisicoes, por_assinatura)
    andamento.itens(len(bundles))
    for bundle in bundles:
        do_bundle, barrados = identificar_no_bundle(bundle, ia)
        andamento.avancar()
        travas_acionadas.extend(barrados)
        for biblioteca in do_bundle:
            if nome_com_versao(biblioteca) not in ja_identificadas:
                anterior = da_ia.get(nome_com_versao(biblioteca))
                da_ia[nome_com_versao(biblioteca)] = preferir_confirmada(anterior, biblioteca)
    return BibliotecasDaIA(list(da_ia.values()), travas_acionadas)


def preferir_confirmada(atual: Biblioteca | None, nova: Biblioteca) -> Biblioteca:
    if atual is None or atual.situacao == "a_confirmar":
        return nova
    return atual


def identificar_no_bundle(
    bundle: Bundle, ia: ClienteDeIA
) -> tuple[list[Biblioteca], list[TravaAcionada]]:
    if not bundle.trechos:
        return [], []
    trechos_enviados = [sanitizar(trecho) for trecho in bundle.trechos]
    prompt = montar_prompt(ARQUIVO_DO_PROMPT, montar_entrada(trechos_enviados))
    resposta = ia.perguntar(ETAPA, prompt)
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


def montar_entrada(trechos: list[str]) -> str:
    blocos = [f"Trecho {numero}:\n~~~\n{trecho}\n~~~" for numero, trecho in enumerate(trechos, 1)]
    return "\n\n".join(blocos)
