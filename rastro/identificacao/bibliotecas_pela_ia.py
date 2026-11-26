from dataclasses import dataclass

from rastro.andamento import ANDAMENTO_SILENCIOSO, Andamento
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
    bibliotecas_por_assinatura: list[Biblioteca],
    cliente_de_ia: ClienteDeIA | None,
    andamento: Andamento = ANDAMENTO_SILENCIOSO,
) -> BibliotecasDaIA:
    if cliente_de_ia is None:
        return BibliotecasDaIA([], [])
    ja_identificadas = {nome_com_versao(biblioteca) for biblioteca in bibliotecas_por_assinatura}
    bibliotecas_da_ia: dict[str, Biblioteca] = {}
    travas_acionadas: list[TravaAcionada] = []
    bundles = escolher_bundles(requisicoes, bibliotecas_por_assinatura)
    andamento.definir_total_de_itens(len(bundles))
    for bundle in bundles:
        bibliotecas_do_bundle, travas_do_bundle = identificar_no_bundle(bundle, cliente_de_ia)
        andamento.avancar_item()
        travas_acionadas.extend(travas_do_bundle)
        for biblioteca in bibliotecas_do_bundle:
            if nome_com_versao(biblioteca) not in ja_identificadas:
                anterior = bibliotecas_da_ia.get(nome_com_versao(biblioteca))
                bibliotecas_da_ia[nome_com_versao(biblioteca)] = preferir_confirmada(
                    anterior, biblioteca
                )
    return BibliotecasDaIA(list(bibliotecas_da_ia.values()), travas_acionadas)


def preferir_confirmada(atual: Biblioteca | None, nova: Biblioteca) -> Biblioteca:
    if atual is None or atual.situacao == "a_confirmar":
        return nova
    return atual


def identificar_no_bundle(
    bundle: Bundle, cliente_de_ia: ClienteDeIA
) -> tuple[list[Biblioteca], list[TravaAcionada]]:
    if not bundle.trechos:
        return [], []
    trechos_enviados = [sanitizar(trecho) for trecho in bundle.trechos]
    prompt = montar_prompt(ARQUIVO_DO_PROMPT, montar_entrada(trechos_enviados))
    resposta = cliente_de_ia.perguntar(ETAPA, prompt)
    if resposta is None:
        return [], []
    sugeridas, travas_acionadas = conferir_formato(tirar_cerca_de_codigo(resposta))
    bibliotecas = []
    for sugerida in sugeridas:
        biblioteca = biblioteca_sugerida(sugerida, bundle.requisicao)
        ancorada, travas_da_ancoragem = conferir_ancoragem(biblioteca, trechos_enviados)
        bibliotecas.append(ancorada)
        travas_acionadas.extend(travas_da_ancoragem)
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
