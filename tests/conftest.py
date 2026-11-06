import socket
from typing import NoReturn

import pytest


class AcessoARedeBloqueado(RuntimeError):
    pass


def recusar_acesso_a_rede(*_argumentos: object, **_opcoes: object) -> NoReturn:
    raise AcessoARedeBloqueado("Os testes não podem acessar a rede (R19.2). Use um dublê.")


@pytest.fixture(autouse=True)
def bloquear_rede(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket.socket, "connect", recusar_acesso_a_rede)
    monkeypatch.setattr(socket.socket, "connect_ex", recusar_acesso_a_rede)
    monkeypatch.setattr(socket, "create_connection", recusar_acesso_a_rede)
    monkeypatch.setattr(socket, "getaddrinfo", recusar_acesso_a_rede)
