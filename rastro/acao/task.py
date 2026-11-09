from rastro.acao.modelos import Acao

AVISO_DO_TESTE_DA_IA = "sugerido pela IA: confira antes de usar"
TESTE_SEM_SUGESTAO = "descrever o teste feito (sem sugestão da IA)"


def gerar_texto_da_task(acao: Acao) -> str:
    linhas = [
        f"## [Rastro] {acao.o_que_fazer}",
        "",
        f"**Por quê:** {acao.porque}",
        f"**Impacto:** {acao.impacto}",
        f"**O que fazer:** {acao.o_que_fazer}. Quem resolve: {acao.quem_resolve}.",
        f"**Critério de aceite:** {criterio_de_aceite(acao)}",
        "",
        "### Evidências",
        "- [ ] Versão (ou configuração) antes e depois",
        f"- [ ] Teste de verificação: {teste_de_verificacao(acao)}",
        "- [ ] Novo HAR sem o achado",
    ]
    return "\n".join(linhas) + "\n"


def criterio_de_aceite(acao: Acao) -> str:
    return f"novo HAR analisado pelo Rastro sem este achado ({', '.join(acao.refs)})."


def teste_de_verificacao(acao: Acao) -> str:
    if acao.teste_verificacao is None:
        return TESTE_SEM_SUGESTAO
    return f"{acao.teste_verificacao} ({AVISO_DO_TESTE_DA_IA})"
