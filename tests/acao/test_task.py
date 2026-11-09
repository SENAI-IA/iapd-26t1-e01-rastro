import json
from pathlib import Path

from rastro.acao.modelos import Acao
from rastro.acao.plano import montar_plano_de_acao
from rastro.acao.task import gerar_texto_da_task
from rastro.configuracao import checagens as regras
from rastro.configuracao.modelos import Checagem
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.github_advisory import converter_resposta
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado
from rastro.risco.nota import calcular_nota
from rastro.travas.faixa_de_versao import descartar_fora_da_faixa

DADOS = Path(__file__).parent.parent / "dados"

JQUERY = Biblioteca(
    pacote="jquery",
    versao="3.4.1",
    metodo="assinatura",
    situacao="confirmada",
    conferida_no_npm=None,
    travas_que_falharam=[],
    evidencias=[],
)


def achados_reais_do_jquery() -> list[Achado]:
    resposta = json.loads((DADOS / "advisory-jquery-3.4.1.json").read_text(encoding="utf-8"))
    avisos, _ = descartar_fora_da_faixa("jquery", "3.4.1", converter_resposta(resposta, "jquery"))
    return [
        Achado(JQUERY, aviso, calcular_nota(aviso.cvss, aviso.percentil_epss)) for aviso in avisos
    ]


def acao(teste_verificacao: str | None = None) -> Acao:
    return Acao(
        id="jquery@3.4.1",
        prioridade="alta",
        nota=7.9,
        o_que_fazer="Atualizar jquery de 3.4.1 para 3.5.0",
        porque="2 falhas conhecidas (GHSA-a, GHSA-b). Nota 7,9 (alta).",
        impacto="Texto do usuário pode virar script na página.",
        quem_resolve="dev front-end",
        refs=["GHSA-a", "GHSA-b"],
        teste_verificacao=teste_verificacao,
    )


def test_r09_1_texto_segue_o_modelo_do_design() -> None:
    texto = gerar_texto_da_task(acao("Colar <img src=x onerror=alert(1)> na busca"))

    assert texto == (
        "## [Rastro] Atualizar jquery de 3.4.1 para 3.5.0\n"
        "\n"
        "**Por quê:** 2 falhas conhecidas (GHSA-a, GHSA-b). Nota 7,9 (alta).\n"
        "**Impacto:** Texto do usuário pode virar script na página.\n"
        "**O que fazer:** Atualizar jquery de 3.4.1 para 3.5.0. Quem resolve: dev front-end.\n"
        "**Critério de aceite:** novo HAR analisado pelo Rastro sem este achado"
        " (GHSA-a, GHSA-b).\n"
        "\n"
        "### Evidências\n"
        "- [ ] Versão (ou configuração) antes e depois\n"
        "- [ ] Teste de verificação: Colar <img src=x onerror=alert(1)> na busca"
        " (sugerido pela IA: confira antes de usar)\n"
        "- [ ] Novo HAR sem o achado\n"
    )


def test_r09_1_sem_explicacao_da_ia_o_texto_sai_completo() -> None:
    texto = montar_plano_de_acao(achados_reais_do_jquery(), {}, [])[0].texto_task

    assert texto.startswith("## [Rastro] Atualizar jquery de 3.4.1 para 3.5.0\n")
    assert "**Por quê:** 2 falhas conhecidas (GHSA-jpcq-cgw6-v4j6, GHSA-gxr4-xjj5-5px2)." in texto
    assert "**Impacto:** " in texto
    assert "**O que fazer:** " in texto
    assert "**Critério de aceite:** " in texto
    assert "- [ ] Teste de verificação: descrever o teste feito (sem sugestão da IA)" in texto
    assert "- [ ] Novo HAR sem o achado" in texto


def test_r09_1_teste_da_explicacao_da_ia_entra_no_checklist() -> None:
    explicacao = Explicacao(
        o_que_e="Falha de XSS",
        impacto="Texto do usuário pode virar script na página.",
        como_corrigir="Atualizar o pacote",
        teste_verificacao="Abrir a página com um texto de teste",
        gerada_por_ia=True,
    )

    acao_do_plano = montar_plano_de_acao(
        achados_reais_do_jquery(), {"jquery@3.4.1": explicacao}, []
    )[0]

    assert acao_do_plano.teste_verificacao == "Abrir a página com um texto de teste"
    assert (
        "- [ ] Teste de verificação: Abrir a página com um texto de teste"
        " (sugerido pela IA: confira antes de usar)" in acao_do_plano.texto_task
    )


def test_r09_1_explicacao_que_nao_veio_da_ia_nao_vira_teste_sugerido() -> None:
    explicacao = Explicacao(
        o_que_e="Resumo do aviso",
        impacto="Resumo do aviso",
        como_corrigir="",
        teste_verificacao="",
        gerada_por_ia=False,
    )

    acao_do_plano = montar_plano_de_acao(
        achados_reais_do_jquery(), {"jquery@3.4.1": explicacao}, []
    )[0]

    assert acao_do_plano.teste_verificacao is None
    assert "sem sugestão da IA" in acao_do_plano.texto_task


def test_r09_1_acao_da_checagem_tambem_ganha_texto_da_task() -> None:
    checagem = Checagem(
        id=regras.CSP_AUSENTE.id,
        titulo=regras.CSP_AUSENTE.titulo,
        situacao="falhou",
        severidade=regras.CSP_AUSENTE.severidade,
        quem_resolve=regras.CSP_AUSENTE.quem_resolve,
        evidencia=None,
        detalhe="a página não envia o cabeçalho: https://loja.exemplo.com/",
    )

    texto = montar_plano_de_acao([], {}, [checagem])[0].texto_task

    assert texto.startswith(
        "## [Rastro] Enviar o cabeçalho Content-Security-Policy nas páginas HTML do site\n"
    )
    assert "**Por quê:** Regra C01 (CSP ausente), severidade média" in texto
    assert "**Critério de aceite:** novo HAR analisado pelo Rastro sem este achado (C01)." in texto
