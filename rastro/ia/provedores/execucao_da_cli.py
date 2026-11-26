import subprocess

from rastro.ia.provedor import FalhaDoProvedor

TEMPO_LIMITE_EM_SEGUNDOS = 120


def executar_cli_da_ia(
    executavel: str, argumentos: list[str], prompt: str, nome_exibido: str
) -> str:
    try:
        processo = subprocess.run(
            [executavel, *argumentos],
            input=prompt,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=TEMPO_LIMITE_EM_SEGUNDOS,
        )
    except subprocess.TimeoutExpired as erro:
        raise FalhaDoProvedor(
            f"a CLI do {nome_exibido} passou do tempo limite de {TEMPO_LIMITE_EM_SEGUNDOS} s"
        ) from erro
    except OSError as erro:
        raise FalhaDoProvedor(f"a CLI do {nome_exibido} não pôde ser executada: {erro}") from erro
    if processo.returncode != 0:
        raise FalhaDoProvedor(
            f"a CLI do {nome_exibido} terminou com código de saída {processo.returncode}"
        )
    return processo.stdout
