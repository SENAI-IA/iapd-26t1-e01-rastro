import re

REMOVIDO = "[removido]"
TAMANHO_MINIMO_DA_CHAVE = 33

JWT = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*")
BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
URL_COM_QUERY_STRING = re.compile(r"\b([a-zA-Z][a-zA-Z0-9+.-]*://[^\s?#\"'`<>]+)\?[^\s#\"'`<>]*")
SEQUENCIA_LONGA = re.compile(rf"[A-Za-z0-9+_-]{{{TAMANHO_MINIMO_DA_CHAVE},}}={{0,2}}")
BASE64_COM_BARRA = re.compile(r"(?<![\w/])(?:[A-Za-z0-9+]{4,}/)+[A-Za-z0-9+]{4,}={0,2}(?![\w/])")


def sanitizar(texto: str) -> str:
    sem_bearer = BEARER.sub(REMOVIDO, texto)
    sem_jwt = JWT.sub(REMOVIDO, sem_bearer)
    sem_query_string = URL_COM_QUERY_STRING.sub(rf"\1?{REMOVIDO}", sem_jwt)
    sem_base64_com_barra = BASE64_COM_BARRA.sub(trocar_se_parece_base64, sem_query_string)
    return SEQUENCIA_LONGA.sub(trocar_se_parece_chave, sem_base64_com_barra)


def trocar_se_parece_chave(sequencia: re.Match[str]) -> str:
    if parece_chave(sequencia.group(0)):
        return REMOVIDO
    return sequencia.group(0)


def trocar_se_parece_base64(sequencia: re.Match[str]) -> str:
    valor = sequencia.group(0)
    if len(valor) >= TAMANHO_MINIMO_DA_CHAVE and parece_base64(valor):
        return REMOVIDO
    return valor


def parece_base64(sequencia: str) -> bool:
    tem_maiuscula = any(caractere.isupper() for caractere in sequencia)
    tem_minuscula = any(caractere.islower() for caractere in sequencia)
    return tem_maiuscula and tem_minuscula and parece_chave(sequencia)


def parece_chave(sequencia: str) -> bool:
    tem_letra = any(caractere.isalpha() for caractere in sequencia)
    tem_digito = any(caractere.isdigit() for caractere in sequencia)
    return tem_letra and tem_digito
