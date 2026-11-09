import subprocess

from rastro.ia.cliente import FalhaDoProvedor, RespostaDoProvedor

OPCOES_SEM_FERRAMENTAS = ["chat", "--no-interactive", "--trust-tools="]
TEMPO_LIMITE_EM_SEGUNDOS = 120


class ProvedorKiro:
    nome = "kiro"

    def __init__(self, executavel: str) -> None:
        self.executavel = executavel

    def executar(self, prompt: str) -> RespostaDoProvedor:
        saida = self.rodar_cli(prompt)
        return ler_resposta(saida)

    def rodar_cli(self, prompt: str) -> str:
        try:
            processo = subprocess.run(
                [self.executavel, *OPCOES_SEM_FERRAMENTAS],
                input=prompt,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=TEMPO_LIMITE_EM_SEGUNDOS,
            )
        except subprocess.TimeoutExpired as erro:
            raise FalhaDoProvedor(
                f"a CLI do Kiro passou do tempo limite de {TEMPO_LIMITE_EM_SEGUNDOS} s"
            ) from erro
        except OSError as erro:
            raise FalhaDoProvedor(f"a CLI do Kiro não pôde ser executada: {erro}") from erro
        if processo.returncode != 0:
            raise FalhaDoProvedor(
                f"a CLI do Kiro terminou com código de saída {processo.returncode}"
            )
        return processo.stdout


def ler_resposta(saida: str) -> RespostaDoProvedor:
    texto = saida.strip()
    if not texto:
        raise FalhaDoProvedor("a CLI do Kiro respondeu sem texto")
    return RespostaDoProvedor(texto, tokens=None)
