from datetime import datetime, timedelta, timezone

import pytest

from rastro.data_e_hora import ler_data_iso


def test_ler_data_iso_entende_o_z_como_utc() -> None:
    assert ler_data_iso("2026-11-20T14:03:00Z") == datetime(
        2026, 11, 20, 14, 3, tzinfo=timezone.utc
    )


def test_ler_data_iso_mantem_o_deslocamento_informado() -> None:
    data = ler_data_iso("2026-11-20T11:03:00-03:00")

    assert data.utcoffset() == timedelta(hours=-3)


def test_ler_data_iso_recusa_texto_que_nao_e_data() -> None:
    with pytest.raises(ValueError):
        ler_data_iso("ontem")
