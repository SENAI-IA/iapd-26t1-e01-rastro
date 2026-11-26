import re

REMOVIDO = "[removido]"
TAMANHO_MINIMO_DA_CHAVE = 33

JWT = re.compile(
    r"""
    \b eyJ [A-Za-z0-9_-]+
    \. [A-Za-z0-9_-]+
    \. [A-Za-z0-9_-]*
    """,
    re.VERBOSE,
)
BEARER = re.compile(
    r"""
    \b Bearer \s+
    [A-Za-z0-9._~+/=-]+
    """,
    re.VERBOSE | re.IGNORECASE,
)
URL_COM_QUERY_STRING = re.compile(
    r"""
    \b
    (?P<endereco>
        [a-zA-Z] [a-zA-Z0-9+.-]* ://
        [^\s?\#"'`<>]+
    )
    \?
    (?P<query> [^\s\#"'`<>]* )
    """,
    re.VERBOSE,
)
LETRAS_DIGITOS_E_SINAIS_DE_CHAVE = "[A-Za-z0-9+_-]"
ENCHIMENTO_DO_BASE64 = "={0,2}"
SEQUENCIA_LONGA = re.compile(
    LETRAS_DIGITOS_E_SINAIS_DE_CHAVE
    + "{"
    + str(TAMANHO_MINIMO_DA_CHAVE)
    + ",}"
    + ENCHIMENTO_DO_BASE64
)
BASE64_COM_BARRA = re.compile(
    r"""
    (?<! [\w/] )
    (?: [A-Za-z0-9+]{4,} / )+
    [A-Za-z0-9+]{4,}
    ={0,2}
    (?! [\w/] )
    """,
    re.VERBOSE,
)


def sanitizar(texto: str) -> str:
    sem_bearer = BEARER.sub(REMOVIDO, texto)
    sem_jwt = JWT.sub(REMOVIDO, sem_bearer)
    sem_query_string = URL_COM_QUERY_STRING.sub(manter_o_endereco_sem_a_query, sem_jwt)
    sem_base64_com_barra = BASE64_COM_BARRA.sub(trocar_se_parece_base64, sem_query_string)
    return SEQUENCIA_LONGA.sub(trocar_se_parece_chave, sem_base64_com_barra)


def manter_o_endereco_sem_a_query(url: re.Match[str]) -> str:
    return url.group("endereco") + "?" + REMOVIDO


def trocar_se_parece_chave(sequencia: re.Match[str]) -> str:
    if parece_chave(sequencia.group()):
        return REMOVIDO
    return sequencia.group()


def trocar_se_parece_base64(sequencia: re.Match[str]) -> str:
    valor = sequencia.group()
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
