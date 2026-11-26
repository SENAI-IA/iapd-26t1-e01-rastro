from rastro.configuracao.falhas_nos_cookies import sem_httponly, sem_samesite, sem_secure
from rastro.har.modelos import Cookie

COOKIE_SEGURO = Cookie("sessao", http_only=True, secure=True, same_site="Lax")
COOKIE_SEM_ATRIBUTOS = Cookie("sessao", http_only=False, secure=False, same_site=None)


def test_r06_6_sem_httponly() -> None:
    assert sem_httponly(COOKIE_SEM_ATRIBUTOS) is True
    assert sem_httponly(COOKIE_SEGURO) is False


def test_r06_6_sem_secure() -> None:
    assert sem_secure(COOKIE_SEM_ATRIBUTOS) is True
    assert sem_secure(COOKIE_SEGURO) is False


def test_r06_6_samesite_ausente_ou_em_branco_falha() -> None:
    assert sem_samesite(COOKIE_SEM_ATRIBUTOS) is True
    assert sem_samesite(Cookie("sessao", http_only=True, secure=True, same_site=" ")) is True
    assert sem_samesite(COOKIE_SEGURO) is False
