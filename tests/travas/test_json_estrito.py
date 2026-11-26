import pytest

from rastro.travas.json_estrito import (
    ForaDoFormato,
    exigir_campos,
    ler_json_sem_texto_fora,
    ler_texto,
    tirar_cerca_de_codigo,
)


def test_r21_1_le_o_json_com_espacos_em_volta() -> None:
    assert ler_json_sem_texto_fora('\n  {"a": 1}\n') == {"a": 1}


@pytest.mark.parametrize(
    ("texto", "motivo"),
    [
        ('Aqui: {"a": 1}', "texto fora do JSON"),
        ('{"a": 1} fim', "texto fora do JSON"),
        ("[1]", "texto fora do JSON"),
        ('{"a": ', "JSON inválido"),
        ('{"a": 1, "a": 2}', "campo repetido: `a`"),
    ],
)
def test_r21_1_recusa_o_que_nao_e_so_um_objeto_json(texto: str, motivo: str) -> None:
    with pytest.raises(ForaDoFormato, match=motivo):
        ler_json_sem_texto_fora(texto)


def test_r21_1_exige_exatamente_os_campos_esperados() -> None:
    assert exigir_campos({"a": 1}, {"a"}, "no item") == {"a": 1}
    with pytest.raises(ForaDoFormato, match="campo a mais no item: b"):
        exigir_campos({"a": 1, "b": 2}, {"a"}, "no item")
    with pytest.raises(ForaDoFormato, match="campo faltando no item: a"):
        exigir_campos({}, {"a"}, "no item")
    with pytest.raises(ForaDoFormato, match="esperado um objeto no item"):
        exigir_campos([], {"a"}, "no item")


def test_r21_1_campo_que_nao_e_texto_e_recusado() -> None:
    assert ler_texto({"a": "x"}, "a") == "x"
    with pytest.raises(ForaDoFormato, match="`a` não é texto"):
        ler_texto({"a": 1}, "a")


@pytest.mark.parametrize(
    ("resposta", "esperado"),
    [
        ('```json\n{"a": 1}\n```', '{"a": 1}'),
        ('```\n{"a": 1}\n```', '{"a": 1}'),
        ('  {"a": 1}  ', '{"a": 1}'),
        ('Veja: ```json\n{"a": 1}\n```', 'Veja: ```json\n{"a": 1}\n```'),
    ],
)
def test_r21_1_tira_so_a_cerca_de_codigo_em_volta_da_resposta(resposta: str, esperado: str) -> None:
    assert tirar_cerca_de_codigo(resposta) == esperado
