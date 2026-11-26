import pytest

from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.pacote_npm import ler_arquivos_de_codigo


def test_r21_5_pacote_corrompido_vira_consulta_nao_realizada() -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_arquivos_de_codigo(b"nao e um tgz")

    assert falha.value.motivo.startswith("pacote ilegível: ")
