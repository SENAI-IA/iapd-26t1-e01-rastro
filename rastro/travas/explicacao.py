import re

from rastro.travas.modelos import TravaAcionada

NOME_DA_TRAVA = "explicação sem fato novo"
PADRAO_DO_CVE = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.IGNORECASE)
PADRAO_DO_GHSA = re.compile(r"\bGHSA(?:-[0-9a-z]{4}){3}\b", re.IGNORECASE)
PADRAO_DA_PORCENTAGEM = re.compile(r"(?<![\d.,])\d+(?:[.,]\d+)?\s?%")
SEM_PORCENTAGEM_DEPOIS = r"(?!\d|\s?%)"
PADRAO_DA_VERSAO = re.compile(
    r"(?<![\d.])\d+(?:\.\d+)+(?:-[A-Za-z][0-9A-Za-z]*(?:\.[0-9A-Za-z]+)*)?"
    + SEM_PORCENTAGEM_DEPOIS
)
PADRAO_DO_DECIMAL_COM_VIRGULA = re.compile(
    r"(?<![\d.,])\d+,\d+(?!,\d)" + SEM_PORCENTAGEM_DEPOIS
)
PADROES_DE_FATO = (
    PADRAO_DO_CVE,
    PADRAO_DO_GHSA,
    PADRAO_DA_PORCENTAGEM,
    PADRAO_DA_VERSAO,
    PADRAO_DO_DECIMAL_COM_VIRGULA,
)


def conferir_explicacao(
    pacote: str, versao: str, explicacao: dict[str, str], entrada_enviada: str
) -> tuple[dict[str, str] | None, list[TravaAcionada]]:
    novos = fatos_novos(explicacao, entrada_enviada)
    if not novos:
        return explicacao, []
    alvo = f"explicação de {pacote}@{versao}"
    motivo = "explicação descartada: cita o que não estava na entrada: " + ", ".join(novos)
    return None, [TravaAcionada(NOME_DA_TRAVA, alvo, motivo)]


def fatos_novos(explicacao: dict[str, str], entrada_enviada: str) -> list[str]:
    fatos_da_entrada = {normalizar(fato) for fato in extrair_fatos(entrada_enviada)}
    novos = []
    for campo, texto in explicacao.items():
        for fato in extrair_fatos(texto):
            citacao = f"`{fato}` ({campo})"
            if normalizar(fato) not in fatos_da_entrada and citacao not in novos:
                novos.append(citacao)
    return novos


def extrair_fatos(texto: str) -> list[str]:
    encontrados: list[re.Match[str]] = []
    for padrao in PADROES_DE_FATO:
        encontrados.extend(padrao.finditer(texto))
    encontrados.sort(key=lambda encontrado: encontrado.start())
    return [encontrado.group() for encontrado in encontrados]


def normalizar(fato: str) -> str:
    return re.sub(r"\s", "", fato).replace(",", ".").upper()
