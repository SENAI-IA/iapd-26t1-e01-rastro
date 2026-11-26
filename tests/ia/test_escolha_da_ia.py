import pytest

from rastro.ia import escolha_da_ia
from rastro.ia.escolha_da_ia import CLIDaIAAusente, IAInvalida, escolher_ia, localizar_cli


def test_r14_1_opcao_ia_vale_antes_da_variavel_de_ambiente() -> None:
    assert escolher_ia("claude", "codex") == "claude"


def test_r14_1_sem_opcao_vale_a_variavel_de_ambiente() -> None:
    assert escolher_ia(None, "codex") == "codex"


@pytest.mark.parametrize("variavel", [None, ""])
def test_r14_1_sem_opcao_nem_variavel_usa_o_kiro(variavel: str | None) -> None:
    assert escolher_ia(None, variavel) == "kiro"


def test_r14_1_nome_da_ia_aceita_maiusculas_e_espacos() -> None:
    assert escolher_ia(" Claude ", None) == "claude"


@pytest.mark.parametrize(
    ("opcao", "variavel", "origem"),
    [("gpt", None, "--ia"), (None, "gemini", "RASTRO_IA"), ("", "claude", "--ia")],
)
def test_r14_2_ia_invalida_lista_as_opcoes_validas(
    opcao: str | None, variavel: str | None, origem: str
) -> None:
    with pytest.raises(IAInvalida) as erro:
        escolher_ia(opcao, variavel)

    assert origem in str(erro.value)
    assert "Opções válidas: kiro, claude, codex." in str(erro.value)


@pytest.mark.parametrize(
    ("nome_da_ia", "executavel"), [("kiro", "kiro-cli"), ("claude", "claude"), ("codex", "codex")]
)
def test_r14_3_procura_o_executavel_de_cada_ia(
    monkeypatch: pytest.MonkeyPatch, nome_da_ia: str, executavel: str
) -> None:
    procurados: list[str] = []

    def which_falso(nome: str) -> str:
        procurados.append(nome)
        return f"/usr/local/bin/{nome}"

    monkeypatch.setattr(escolha_da_ia.shutil, "which", which_falso)

    assert localizar_cli(nome_da_ia) == f"/usr/local/bin/{executavel}"
    assert procurados == [executavel]


def test_r14_3_cli_ausente_diz_qual_faltou(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(escolha_da_ia.shutil, "which", lambda _nome: None)

    with pytest.raises(CLIDaIAAusente) as erro:
        localizar_cli("kiro")

    assert "kiro-cli" in str(erro.value)
