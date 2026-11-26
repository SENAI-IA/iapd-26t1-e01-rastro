import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from rastro.cli import executar
from rastro.fluxo_da_analise import analisar
from rastro.fontes import osv
from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.github_advisory import converter_resposta
from rastro.fontes.modelos import Aviso
from rastro.ia.cliente import ClienteDeIA, FalhaDoProvedor, RespostaDoProvedor
from rastro.modelos_da_analise import Analise
from rastro.pentest.sonda import RespostaHttp
from rastro.relatorio.montagem_do_relatorio import montar_relatorio

DADOS = Path(__file__).parent / "dados"
HAR_DA_LOJA = DADOS / "loja.har"
PASTA_DA_LOJA = Path("loja.exemplo.com") / "2026-11-20_14-03-00"
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


def aviso_do_jquery_fora_da_faixa() -> Aviso:
    return replace(
        avisos_gravados_do_jquery()[0],
        ghsa="GHSA-rmxg-73gg-4p98",
        apelidos=[],
        cve=None,
        versoes_afetadas="< 1.9.0",
        versao_corrigida="1.9.0",
        link="https://github.com/advisories/GHSA-rmxg-73gg-4p98",
    )


class ConectorFalso:
    def __init__(self, sem_resposta_para: frozenset[str] = frozenset()) -> None:
        self.sem_resposta_para = sem_resposta_para
        self.consultas: list[tuple[str, str]] = []

    def consultar(self, pacote: str, versao: str) -> list[Aviso]:
        self.consultas.append((pacote, versao))
        if pacote in self.sem_resposta_para:
            raise ConsultaNaoRealizada("sem resposta do GitHub Advisory: tempo esgotado")
        if pacote == "jquery":
            return [*avisos_gravados_do_jquery(), aviso_do_jquery_fora_da_faixa()]
        return []


def avisos_gravados_do_jquery_no_osv() -> list[Aviso]:
    with (DADOS / "osv-jquery-3.4.1.json").open(encoding="utf-8") as arquivo:
        return osv.converter_resposta(json.load(arquivo), "jquery")


class OsvFalso:
    def __init__(self, sem_resposta: bool = False) -> None:
        self.sem_resposta = sem_resposta
        self.consultas: list[tuple[str, str]] = []

    def consultar(self, pacote: str, versao: str) -> list[Aviso]:
        self.consultas.append((pacote, versao))
        if self.sem_resposta:
            raise ConsultaNaoRealizada("sem resposta do OSV: tempo esgotado")
        if pacote == "jquery":
            return avisos_gravados_do_jquery_no_osv()
        return []


class NvdFalso:
    def __init__(
        self, cvss: dict[str, float | None] | None = None, falhas: dict[str, str] | None = None
    ) -> None:
        self.cvss = cvss or {}
        self.falhas = falhas or {}
        self.consultados: list[str] = []

    def buscar_cvss(self, cve: str) -> float | None:
        self.consultados.append(cve)
        if cve in self.falhas:
            raise ConsultaNaoRealizada(self.falhas[cve])
        return self.cvss.get(cve)


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


class SondaFalsa:
    def __init__(self, respostas: list[RespostaHttp]) -> None:
        self.respostas = list(respostas)
        self.chamadas: list[tuple[str, str, str | None]] = []

    def sondar(self, url: str, metodo: str, origem: str | None) -> RespostaHttp:
        self.chamadas.append((url, metodo, origem))
        return self.respostas.pop(0)


class NavegadorFalso:
    def __init__(self, abre: bool) -> None:
        self.abre = abre
        self.enderecos: list[str] = []

    def __call__(self, endereco: str) -> bool:
        self.enderecos.append(endereco)
        return self.abre


def ler_relatorio(caminho: Path) -> dict[str, Any]:
    with caminho.open(encoding="utf-8") as arquivo:
        dados: dict[str, Any] = json.load(arquivo)
    return dados


def analisar_loja(saida: Path) -> int:
    return executar(["analisar", str(HAR_DA_LOJA), "--sem-ia", "--saida", str(saida)])


def analise_da_loja(fonte: ConectorFalso | None = None) -> Analise:
    return analisar(HAR_DA_LOJA, fonte or ConectorFalso(), RegistroFalso())


def relatorio_da_loja() -> dict[str, Any]:
    return montar_relatorio(analise_da_loja())


def analise_da_loja_com_ia(*respostas: RespostaDoProvedor | FalhaDoProvedor) -> Analise:
    ia = ClienteDeIA(ProvedorFalso(list(respostas), nome="kiro"))
    return analisar(HAR_DA_LOJA, ConectorFalso(), RegistroFalso(), ia)
