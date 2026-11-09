import json
from pathlib import Path

from rastro.fontes.conector import Aviso, ConsultaNaoRealizada
from rastro.fontes.github_advisory import converter_resposta

DADOS = Path(__file__).parent / "dados"
HAR_DA_LOJA = DADOS / "loja.har"


def avisos_gravados_do_jquery() -> list[Aviso]:
    with (DADOS / "advisory-jquery-3.4.1.json").open(encoding="utf-8") as arquivo:
        return converter_resposta(json.load(arquivo), "jquery")


class ConectorFalso:
    def __init__(self, sem_resposta_para: frozenset[str] = frozenset()) -> None:
        self.sem_resposta_para = sem_resposta_para
        self.consultas: list[tuple[str, str]] = []

    def consultar(self, pacote: str, versao: str) -> list[Aviso]:
        self.consultas.append((pacote, versao))
        if pacote in self.sem_resposta_para:
            raise ConsultaNaoRealizada("sem resposta do GitHub Advisory: tempo esgotado")
        if pacote == "jquery":
            return avisos_gravados_do_jquery()
        return []


class RegistroFalso:
    def __init__(self, nao_publicados: frozenset[str] = frozenset()) -> None:
        self.nao_publicados = nao_publicados
        self.consultas: list[tuple[str, str]] = []

    def existe(self, pacote: str, versao: str) -> bool:
        self.consultas.append((pacote, versao))
        return pacote not in self.nao_publicados
