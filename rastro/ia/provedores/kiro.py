from rastro.ia.provedor import FalhaDoProvedor, RespostaDoProvedor
from rastro.ia.provedores.execucao_da_cli import executar_cli_da_ia

OPCOES_SEM_FERRAMENTAS = ["chat", "--no-interactive", "--trust-tools="]


class ProvedorKiro:
    nome = "kiro"

    def __init__(self, executavel: str) -> None:
        self.executavel = executavel

    def executar(self, prompt: str) -> RespostaDoProvedor:
        saida = executar_cli_da_ia(self.executavel, OPCOES_SEM_FERRAMENTAS, prompt, "Kiro")
        return ler_resposta(saida)


def ler_resposta(saida: str) -> RespostaDoProvedor:
    texto = saida.strip()
    if not texto:
        raise FalhaDoProvedor("a CLI do Kiro respondeu sem texto")
    return RespostaDoProvedor(texto, tokens=None)
