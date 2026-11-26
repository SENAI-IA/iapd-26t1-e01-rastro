from pathlib import Path
from typing import Any

from rastro.comandos.comando_pentest import texto_do_resumo_do_pentest
from rastro.comandos.navegador import abrir_relatorio
from rastro.relatorio.gravacao import RelatorioGravado
from rastro.risco.nota import escrever_nota
from rastro.risco.prioridade import PRIORIDADES, ROTULO_DA_PRIORIDADE

AVISO_SEM_IA = (
    "Atenção: análise sem IA. Bibliotecas em bundles não foram procuradas; "
    "podem existir falhas que não aparecem aqui."
)
TEXTO_PENTEST_NO_RELATORIO = (
    "Segurança ativa: {resumo}, na aba Segurança ativa. Não muda a nota nem o plano de ação."
)


def mostrar_resultado(
    pasta: Path, gravado: RelatorioGravado, relatorio: dict[str, Any], abrir: bool
) -> None:
    print(f"Relatório gravado em: {pasta}")
    print(f"HTML: {gravado.html}")
    print(f"JSON: {gravado.json}")
    print(f"Resumo: {resumo_de_uma_linha(relatorio)}")
    if relatorio["pentest"] is not None:
        resumo = texto_do_resumo_do_pentest(relatorio["pentest"]["resumo"])
        print(TEXTO_PENTEST_NO_RELATORIO.format(resumo=resumo))
    if abrir:
        abrir_relatorio(gravado.html)
    if relatorio["analise"]["ia"] is None:
        print(AVISO_SEM_IA)
    for texto in falhas_da_ia(relatorio):
        print(f"Atenção: {texto}")


def falhas_da_ia(relatorio: dict[str, Any]) -> list[str]:
    limitacoes = relatorio["analise"]["limitacoes"]
    return [item["texto"] for item in limitacoes if item["id"].startswith("ia_falhou_")]


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
    return ", ".join(f"{contagem[p]} {ROTULO_DA_PRIORIDADE[p]}" for p in PRIORIDADES)
