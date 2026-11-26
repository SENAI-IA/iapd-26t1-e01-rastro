from pathlib import Path
from typing import Any

from rastro.comandos.navegador import abrir_relatorio
from rastro.pentest.resumo_do_pentest import texto_do_resumo_do_pentest
from rastro.relatorio.gravacao_do_relatorio import RelatorioGravado
from rastro.risco.nota import escrever_nota
from rastro.risco.prioridade import PRIORIDADES, ROTULO_DA_PRIORIDADE

PREFIXO_DA_FALHA_DA_IA = "ia_falhou_"
AVISO_SEM_IA = (
    "Atenção: análise sem IA. Bibliotecas em bundles não foram procuradas; "
    "podem existir falhas que não aparecem aqui."
)
TEXTO_PENTEST_NO_RELATORIO = (
    "Segurança ativa: {resumo}, na aba Segurança ativa. Não muda a nota nem o plano de ação."
)


def mostrar_resultado(
    pasta: Path,
    arquivos_gravados: RelatorioGravado,
    relatorio: dict[str, Any],
    abrir_no_navegador: bool,
) -> None:
    print(f"Relatório gravado em: {pasta}")
    print(f"HTML: {arquivos_gravados.html}")
    print(f"JSON: {arquivos_gravados.json}")
    print(f"Resumo: {resumo_de_uma_linha(relatorio)}")
    if relatorio["pentest"] is not None:
        resumo = texto_do_resumo_do_pentest(relatorio["pentest"]["resumo"])
        print(TEXTO_PENTEST_NO_RELATORIO.format(resumo=resumo))
    if abrir_no_navegador:
        abrir_relatorio(arquivos_gravados.html)
    if relatorio["analise"]["ia"] is None:
        print(AVISO_SEM_IA)
    for texto in falhas_da_ia(relatorio):
        print(f"Atenção: {texto}")


def falhas_da_ia(relatorio: dict[str, Any]) -> list[str]:
    limitacoes = relatorio["analise"]["limitacoes"]
    return [item["texto"] for item in limitacoes if limitacao_de_falha_da_ia(item)]


def limitacao_de_falha_da_ia(limitacao: dict[str, str]) -> bool:
    return limitacao["id"].startswith(PREFIXO_DA_FALHA_DA_IA)


def resumo_de_uma_linha(relatorio: dict[str, Any]) -> str:
    resumo = relatorio["resumo"]
    site = relatorio["analise"]["site"] or relatorio["analise"]["har"]
    partes = [
        site,
        f"bibliotecas: {resumo['bibliotecas']} ({resumo['bibliotecas_vulneraveis']} com falhas)",
        f"achados: {resumo['achados']}",
        f"nota máxima: {escrever_nota_maxima(resumo['nota_maxima'])}",
        f"ações: {resumo['acoes']} ({escrever_acoes_por_prioridade(resumo)})",
    ]
    return " · ".join(partes)


def escrever_nota_maxima(nota: float | None) -> str:
    if nota is None:
        return "sem nota"
    return escrever_nota(nota)


def escrever_acoes_por_prioridade(resumo: dict[str, Any]) -> str:
    contagem = resumo["acoes_por_prioridade"]
    return ", ".join(
        f"{contagem[prioridade]} {ROTULO_DA_PRIORIDADE[prioridade]}" for prioridade in PRIORIDADES
    )
