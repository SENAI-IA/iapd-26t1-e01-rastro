from rastro.ia.provedores.contagem_de_tokens import somar_tokens

CAMPOS = ("input_tokens", "output_tokens")


def test_r11_1_soma_os_tokens_dos_campos_informados() -> None:
    assert somar_tokens({"input_tokens": 10, "output_tokens": 5, "outro": 99}, CAMPOS) == 15


def test_r11_2_uso_que_nao_e_dicionario_fica_sem_tokens() -> None:
    assert somar_tokens(None, CAMPOS) is None


def test_r11_2_campo_ausente_fica_sem_tokens_sem_estimar() -> None:
    assert somar_tokens({"input_tokens": 10}, CAMPOS) is None


def test_r11_2_contagem_negativa_booleana_ou_texto_fica_sem_tokens() -> None:
    assert somar_tokens({"input_tokens": -1, "output_tokens": 5}, CAMPOS) is None
    assert somar_tokens({"input_tokens": True, "output_tokens": 5}, CAMPOS) is None
    assert somar_tokens({"input_tokens": "10", "output_tokens": 5}, CAMPOS) is None
