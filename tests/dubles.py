import json
from pathlib import Path

from rastro.fontes.conector import Aviso, ConsultaNaoRealizada
from rastro.fontes.github_advisory import converter_resposta
from rastro.ia.cliente import FalhaDoProvedor, RespostaDoProvedor

DADOS = Path(__file__).parent / "dados"
HAR_DA_LOJA = DADOS / "loja.har"
HAR_DO_JUICE_SHOP = Path(__file__).parent.parent / "avaliacao" / "juiceshop.har"
TRECHO_DO_ANGULAR = "[`ng-version`,`22.2.2`]"
CODIGOS_PUBLICADOS = {
    ("@angular/core", "22.2.2"): [
        "const NG_VERSION_ATTR_NAME = 'ng-version';",
        "const VERSION = new Version('22.2.2');",
    ],
    ("@fortawesome/fontawesome-free", "5.15.4"): ['var UNITS_PER_EM = "FA \\"5.15.4\\"";'],
}


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
        self.leituras: list[tuple[str, str]] = []

    def existe(self, pacote: str, versao: str) -> bool:
        self.consultas.append((pacote, versao))
        return pacote not in self.nao_publicados

    def ler_codigo(self, pacote: str, versao: str) -> list[str]:
        self.leituras.append((pacote, versao))
        if (pacote, versao) not in CODIGOS_PUBLICADOS:
            raise ConsultaNaoRealizada("pacote fora do dublê")
        return CODIGOS_PUBLICADOS[(pacote, versao)]


class ProvedorFalso:
    def __init__(
        self,
        respostas: list[RespostaDoProvedor | FalhaDoProvedor] | None = None,
        nome: str = "falso",
    ) -> None:
        self.nome = nome
        self.respostas = list(respostas or [])
        self.prompts: list[str] = []

    def executar(self, prompt: str) -> RespostaDoProvedor:
        self.prompts.append(prompt)
        resposta = self.respostas.pop(0)
        if isinstance(resposta, FalhaDoProvedor):
            raise resposta
        return resposta
