from rastro.ia.montagem_do_prompt import MARCADOR_DA_ENTRADA, montar_prompt

ENTRADA_COM_CHAVES = '{"pacote": "jquery", "versao": "3.4.1"}'


def test_r07_2_entrada_entra_no_lugar_do_marcador() -> None:
    prompt = montar_prompt("explicar_achado.md", ENTRADA_COM_CHAVES)

    assert ENTRADA_COM_CHAVES in prompt
    assert MARCADOR_DA_ENTRADA not in prompt


def test_r03_1_le_o_prompt_versionado_da_pasta_de_prompts() -> None:
    prompt = montar_prompt("identificar_bibliotecas.md", "trechos")

    assert prompt.startswith("# ")
    assert prompt.rstrip().endswith("trechos")


def test_r07_2_chaves_do_exemplo_de_json_ficam_intactas() -> None:
    prompt = montar_prompt("explicar_achado.md", "entrada")

    assert '"pacote": "biblioteca-exemplo"' in prompt
