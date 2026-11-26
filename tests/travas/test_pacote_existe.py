from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.identificacao.modelos import Biblioteca, MetodoDeIdentificacao
from rastro.travas.modelos import TravaAcionada
from rastro.travas.pacote_existe import conferir_pacote_no_npm

PUBLICADOS = {("jquery", "3.4.1")}


class RegistroFalso:
    def __init__(self, motivo_sem_resposta: str | None = None) -> None:
        self.motivo_sem_resposta = motivo_sem_resposta

    def existe(self, pacote: str, versao: str) -> bool:
        if self.motivo_sem_resposta is not None:
            raise ConsultaNaoRealizada(self.motivo_sem_resposta)
        return (pacote, versao) in PUBLICADOS

    def ler_codigo(self, pacote: str, versao: str) -> list[str]:
        raise AssertionError("a trava do pacote não lê o código")


def biblioteca(versao: str = "3.4.1", metodo: MetodoDeIdentificacao = "ia") -> Biblioteca:
    return Biblioteca(
        pacote="jquery",
        versao=versao,
        metodo=metodo,
        situacao="confirmada",
        conferida_no_npm=None,
        travas_que_falharam=[],
        evidencias=[],
    )


def test_r21_4_pacote_publicado_passa_marcado_como_conferido() -> None:
    conferida, trava_acionada = conferir_pacote_no_npm(biblioteca(), RegistroFalso())

    assert conferida.situacao == "confirmada"
    assert conferida.conferida_no_npm is True
    assert trava_acionada is None


def test_r21_4_versao_inventada_pela_ia_e_barrada() -> None:
    conferida, trava_acionada = conferir_pacote_no_npm(biblioteca("9.9.9"), RegistroFalso())

    assert conferida.situacao == "a_confirmar"
    assert conferida.conferida_no_npm is False
    assert conferida.travas_que_falharam == ["pacote existe"]
    assert trava_acionada == TravaAcionada(
        "pacote existe", "jquery@9.9.9", "jquery@9.9.9 não foi publicado no npm"
    )


def test_r21_9_sem_resposta_so_a_biblioteca_da_ia_e_barrada() -> None:
    registro = RegistroFalso("sem rede")

    biblioteca_por_assinatura, sem_trava = conferir_pacote_no_npm(
        biblioteca(metodo="assinatura"), registro
    )
    biblioteca_da_ia, trava_acionada = conferir_pacote_no_npm(biblioteca(), registro)

    assert biblioteca_por_assinatura.situacao == "confirmada"
    assert biblioteca_por_assinatura.conferida_no_npm is None
    assert sem_trava is None
    assert biblioteca_da_ia.situacao == "a_confirmar"
    assert trava_acionada is not None
    assert trava_acionada.motivo == "não foi possível conferir no npm: sem rede"
