from rastro.acao.acoes_das_bibliotecas import (
    acoes_das_bibliotecas,
    escrever_nota_da_acao,
    identificadores_dos_avisos,
    impacto_da_biblioteca,
    maior_das_versoes_corrigidas,
    menor_versao_que_corrige_todos,
    o_que_fazer_na_biblioteca,
    porque_da_biblioteca,
    tem_teste_sugerido_pela_ia,
)
from rastro.acao.acoes_das_bibliotecas import (
    teste_sugerido_pela_ia as sugestao_de_teste_da_ia,
)
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.modelos import Aviso
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado
from rastro.risco.nota import calcular_nota

JQUERY = Biblioteca(
    pacote="jquery",
    versao="3.4.1",
    metodo="assinatura",
    situacao="confirmada",
    conferida_no_npm=None,
    travas_que_falharam=[],
    evidencias=[],
)


def aviso(ghsa: str, versao_corrigida: str | None) -> Aviso:
    return Aviso(
        fontes=["GitHub Advisory"],
        apelidos=[],
        ghsa=ghsa,
        cve=None,
        resumo=f"Resumo do {ghsa}",
        cvss=6.1,
        percentil_epss=0.5,
        versoes_afetadas="< 99.0.0",
        versao_corrigida=versao_corrigida,
        link=f"https://github.com/advisories/{ghsa}",
    )


def explicacao(gerada_por_ia: bool, teste_verificacao: str) -> Explicacao:
    return Explicacao(
        o_que_e="Falha de XSS",
        impacto="Texto do usuário vira script.",
        como_corrigir="Atualizar",
        teste_verificacao=teste_verificacao,
        gerada_por_ia=gerada_por_ia,
    )


def test_r08_1_uma_acao_por_biblioteca_com_a_explicacao_dela() -> None:
    achados = [Achado(JQUERY, aviso("GHSA-a", "3.5.0"), calcular_nota(6.1, 0.5))]
    explicacoes = {"jquery@3.4.1": explicacao(True, "Abrir a página")}

    acoes = acoes_das_bibliotecas(achados, explicacoes)

    assert [acao.id for acao in acoes] == ["jquery@3.4.1"]
    assert acoes[0].impacto == "Texto do usuário vira script."
    assert acoes[0].teste_verificacao == "Abrir a página"


def test_r08_1_menor_versao_que_corrige_todos_e_a_maior_das_corrigidas() -> None:
    avisos = [aviso("GHSA-a", "3.5.0"), aviso("GHSA-b", "3.10.0"), aviso("GHSA-c", None)]

    assert menor_versao_que_corrige_todos(avisos) == "3.10.0"
    assert maior_das_versoes_corrigidas(["3.5.0", "3.10.0", "3.9.1"]) == "3.10.0"


def test_r08_4_sem_versao_corrigida_nao_ha_versao_alvo() -> None:
    assert menor_versao_que_corrige_todos([aviso("GHSA-a", None)]) is None


def test_r08_4_o_que_fazer_avisa_o_aviso_sem_correcao() -> None:
    avisos = [aviso("GHSA-a", "3.5.0"), aviso("GHSA-b", None)]

    assert o_que_fazer_na_biblioteca(JQUERY, avisos) == (
        "Atualizar jquery de 3.4.1 para 3.5.0; "
        "GHSA-b sem correção publicada: avaliar troca ou mitigação"
    )


def test_r08_3_identificadores_dos_avisos_sem_repetir_e_na_ordem() -> None:
    avisos = [aviso("GHSA-b", None), aviso("GHSA-a", None), aviso("GHSA-b", None)]

    assert identificadores_dos_avisos(avisos) == ["GHSA-b", "GHSA-a"]


def test_r08_3_porque_conta_as_falhas_e_traz_a_nota() -> None:
    assert porque_da_biblioteca([aviso("GHSA-a", None)], 7.9, "alta") == (
        "1 falha conhecida (GHSA-a). Nota 7,9 (alta)."
    )
    assert escrever_nota_da_acao(None, "a avaliar") == "Sem nota, falta CVSS (a avaliar)"


def test_r08_3_impacto_sem_explicacao_vem_do_resumo_do_primeiro_aviso() -> None:
    avisos = [aviso("GHSA-a", None), aviso("GHSA-b", None)]

    assert impacto_da_biblioteca(avisos, None) == "Resumo do GHSA-a"


def test_r07_4_teste_de_verificacao_so_entra_quando_a_ia_sugeriu() -> None:
    assert sugestao_de_teste_da_ia(explicacao(True, "Abrir a página")) == "Abrir a página"
    assert sugestao_de_teste_da_ia(explicacao(False, "Abrir a página")) is None
    assert sugestao_de_teste_da_ia(explicacao(True, "")) is None
    assert sugestao_de_teste_da_ia(None) is None
    assert tem_teste_sugerido_pela_ia(explicacao(True, "Abrir a página")) is True
