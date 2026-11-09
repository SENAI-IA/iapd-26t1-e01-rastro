from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.identificacao.modelos import Biblioteca, Evidencia, MetodoDeIdentificacao
from rastro.travas.conferencia import conferir_bibliotecas
from rastro.travas.modelos import TravaAcionada

PUBLICADOS = {("jquery", "3.4.1"), ("@angular/core", "11.0.0")}


class RegistroFalso:
    def __init__(self, motivo_sem_resposta: str | None = None) -> None:
        self.motivo_sem_resposta = motivo_sem_resposta
        self.consultas: list[tuple[str, str]] = []

    def existe(self, pacote: str, versao: str) -> bool:
        self.consultas.append((pacote, versao))
        if self.motivo_sem_resposta is not None:
            raise ConsultaNaoRealizada(self.motivo_sem_resposta)
        return (pacote, versao) in PUBLICADOS


def biblioteca(
    pacote: str, versao: str, metodo: MetodoDeIdentificacao = "assinatura"
) -> Biblioteca:
    return Biblioteca(
        pacote=pacote,
        versao=versao,
        metodo=metodo,
        situacao="confirmada",
        conferida_no_npm=None,
        travas_que_falharam=[],
        evidencias=[Evidencia(indice_requisicao=0, url="https://site/jquery.js", trecho=None)],
    )


def test_r21_4_pacote_publicado_fica_confirmado_e_conferido() -> None:
    registro = RegistroFalso()

    conferidas = conferir_bibliotecas([biblioteca("jquery", "3.4.1")], registro)

    jquery = conferidas.confirmadas[0]
    assert jquery.situacao == "confirmada"
    assert jquery.conferida_no_npm is True
    assert jquery.travas_que_falharam == []
    assert conferidas.a_confirmar == []
    assert conferidas.travas_acionadas == []
    assert registro.consultas == [("jquery", "3.4.1")]


def test_r21_4_versao_nao_publicada_vai_para_a_confirmar() -> None:
    conferidas = conferir_bibliotecas([biblioteca("jquery", "9.9.9")], RegistroFalso())

    jquery = conferidas.a_confirmar[0]
    assert conferidas.confirmadas == []
    assert jquery.situacao == "a_confirmar"
    assert jquery.conferida_no_npm is False
    assert jquery.travas_que_falharam == ["pacote existe"]


def test_r21_4_pacote_barrado_fica_registrado_com_o_motivo() -> None:
    conferidas = conferir_bibliotecas([biblioteca("jquery", "9.9.9")], RegistroFalso())

    assert conferidas.travas_acionadas == [
        TravaAcionada("pacote existe", "jquery@9.9.9", "jquery@9.9.9 não foi publicado no npm")
    ]


def test_r21_4_pacote_inventado_pela_ia_vai_para_a_confirmar() -> None:
    inventado = biblioteca("jquery-pro", "3.4.1", metodo="ia")

    conferidas = conferir_bibliotecas([inventado], RegistroFalso())

    assert conferidas.a_confirmar[0].travas_que_falharam == ["pacote existe"]
    assert conferidas.confirmadas == []


def test_r21_4_separa_confirmadas_e_a_confirmar_na_ordem_recebida() -> None:
    bibliotecas = [
        biblioteca("jquery", "9.9.9"),
        biblioteca("@angular/core", "11.0.0"),
        biblioteca("jquery", "3.4.1"),
    ]

    conferidas = conferir_bibliotecas(bibliotecas, RegistroFalso())

    assert [b.pacote for b in conferidas.confirmadas] == ["@angular/core", "jquery"]
    assert [(b.pacote, b.versao) for b in conferidas.a_confirmar] == [("jquery", "9.9.9")]


def test_r21_9_sem_resposta_assinatura_segue_nao_conferida_no_npm() -> None:
    registro = RegistroFalso("sem resposta do registro do npm: sem rede")

    conferidas = conferir_bibliotecas([biblioteca("jquery", "3.4.1")], registro)

    jquery = conferidas.confirmadas[0]
    assert jquery.situacao == "confirmada"
    assert jquery.conferida_no_npm is None
    assert jquery.travas_que_falharam == []
    assert conferidas.travas_acionadas == []


def test_r21_9_sem_resposta_biblioteca_da_ia_vai_para_a_confirmar() -> None:
    registro = RegistroFalso("sem resposta do registro do npm: sem rede")

    conferidas = conferir_bibliotecas([biblioteca("jquery", "3.4.1", metodo="ia")], registro)

    jquery = conferidas.a_confirmar[0]
    assert jquery.conferida_no_npm is None
    assert jquery.travas_que_falharam == ["pacote existe"]
    assert conferidas.travas_acionadas == [
        TravaAcionada(
            "pacote existe",
            "jquery@3.4.1",
            "não foi possível conferir no npm: sem resposta do registro do npm: sem rede",
        )
    ]
