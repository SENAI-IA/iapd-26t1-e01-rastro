from urllib.parse import urlsplit

ESQUEMAS_ACEITOS = ("http", "https")
PORTAS_PADRAO = {"http": 80, "https": 443}


class UrlInvalida(Exception):
    def __init__(self, url: str) -> None:
        super().__init__(
            "a URL precisa começar com http:// ou https://, como https://site.com.br: "
            f"{url_sem_usuario_e_senha(url)}"
        )


def host_da_url(url: str) -> str:
    partes = urlsplit(url)
    if partes.scheme not in ESQUEMAS_ACEITOS or not partes.hostname:
        raise UrlInvalida(url)
    try:
        porta = partes.port
    except ValueError as erro:
        raise UrlInvalida(url) from erro
    host = entre_colchetes_se_for_ipv6(partes.hostname)
    if porta is None or porta == PORTAS_PADRAO[partes.scheme]:
        return host
    return f"{host}:{porta}"


def entre_colchetes_se_for_ipv6(host: str) -> str:
    if ":" in host:
        return f"[{host}]"
    return host


def url_sem_usuario_e_senha(url: str) -> str:
    partes = urlsplit(url)
    if partes.username is None and partes.password is None:
        return url
    host_e_porta = host_e_porta_sem_usuario_e_senha(partes.netloc)
    return partes._replace(netloc=host_e_porta).geturl()


def motivo_sem_usuario_e_senha(motivo: str, url: str) -> str:
    return motivo.replace(url, url_sem_usuario_e_senha(url))


def host_e_porta_sem_usuario_e_senha(netloc: str) -> str:
    _, host_e_porta = netloc.rsplit("@", 1)
    return host_e_porta
