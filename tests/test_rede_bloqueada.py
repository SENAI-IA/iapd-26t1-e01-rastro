import socket
import urllib.request

import pytest

from tests.conftest import AcessoARedeBloqueado


def test_r19_2_conexao_direta_e_bloqueada() -> None:
    with pytest.raises(AcessoARedeBloqueado):
        socket.create_connection(("api.github.com", 443))


def test_r19_2_urlopen_e_bloqueado() -> None:
    with pytest.raises(AcessoARedeBloqueado):
        urllib.request.urlopen("https://api.github.com", timeout=5)


def test_r19_2_socket_manual_e_bloqueado() -> None:
    with socket.socket() as conexao, pytest.raises(AcessoARedeBloqueado):
        conexao.connect(("127.0.0.1", 9))
