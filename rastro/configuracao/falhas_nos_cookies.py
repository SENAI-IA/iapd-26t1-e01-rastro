from rastro.har.modelos import Cookie


def sem_httponly(cookie: Cookie) -> bool:
    return not cookie.http_only


def sem_secure(cookie: Cookie) -> bool:
    return not cookie.secure


def sem_samesite(cookie: Cookie) -> bool:
    return not (cookie.same_site or "").strip()
