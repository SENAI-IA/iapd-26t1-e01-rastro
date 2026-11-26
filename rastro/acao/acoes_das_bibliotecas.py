from rastro.acao.modelos import Acao
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.modelos import Aviso
from rastro.identificacao.modelos import Biblioteca
from rastro.listas import sem_repeticao
from rastro.risco.achados import agrupar_por_biblioteca
from rastro.risco.modelos import Achado, Prioridade
from rastro.risco.nota import escrever_nota
from rastro.risco.prioridade import (
    ROTULO_DA_PRIORIDADE,
    classificar_prioridade,
    nota_da_biblioteca,
    ordenar_achados,
)
from rastro.versao_semver import ler_versao

QUEM_RESOLVE_A_BIBLIOTECA = "dev front-end"
SEM_CORRECAO_PUBLICADA = "sem correção publicada: avaliar troca ou mitigação"


def acoes_das_bibliotecas(achados: list[Achado], explicacoes: dict[str, Explicacao]) -> list[Acao]:
    acoes = []
    for chave_da_biblioteca, achados_da_biblioteca in agrupar_por_biblioteca(achados).items():
        explicacao = explicacoes.get(chave_da_biblioteca)
        acoes.append(acao_da_biblioteca(chave_da_biblioteca, achados_da_biblioteca, explicacao))
    return acoes


def acao_da_biblioteca(
    chave_da_biblioteca: str, achados_da_biblioteca: list[Achado], explicacao: Explicacao | None
) -> Acao:
    achados_em_ordem = ordenar_achados(achados_da_biblioteca)
    biblioteca = achados_em_ordem[0].biblioteca
    avisos = [achado.aviso for achado in achados_em_ordem]
    nota = nota_da_biblioteca(achados_em_ordem)
    prioridade = classificar_prioridade(nota)
    return Acao(
        id=chave_da_biblioteca,
        prioridade=prioridade,
        nota=nota,
        o_que_fazer=o_que_fazer_na_biblioteca(biblioteca, avisos),
        porque=porque_da_biblioteca(avisos, nota, prioridade),
        impacto=impacto_da_biblioteca(avisos, explicacao),
        quem_resolve=QUEM_RESOLVE_A_BIBLIOTECA,
        refs=identificadores_dos_avisos(avisos),
        teste_verificacao=teste_sugerido_pela_ia(explicacao),
    )


def o_que_fazer_na_biblioteca(biblioteca: Biblioteca, avisos: list[Aviso]) -> str:
    versao_alvo = menor_versao_que_corrige_todos(avisos)
    sem_correcao = identificadores_dos_avisos(avisos_sem_correcao(avisos))
    if versao_alvo is None:
        return f"{biblioteca.pacote} {biblioteca.versao} {SEM_CORRECAO_PUBLICADA}"
    atualizar = f"Atualizar {biblioteca.pacote} de {biblioteca.versao} para {versao_alvo}"
    if sem_correcao:
        return f"{atualizar}; {', '.join(sem_correcao)} {SEM_CORRECAO_PUBLICADA}"
    return atualizar


def menor_versao_que_corrige_todos(avisos: list[Aviso]) -> str | None:
    versoes_corrigidas = [aviso.versao_corrigida for aviso in avisos if aviso.versao_corrigida]
    if not versoes_corrigidas:
        return None
    return maior_das_versoes_corrigidas(versoes_corrigidas)


def maior_das_versoes_corrigidas(versoes_corrigidas: list[str]) -> str:
    return max(versoes_corrigidas, key=ler_versao)


def avisos_sem_correcao(avisos: list[Aviso]) -> list[Aviso]:
    return [aviso for aviso in avisos if not aviso.versao_corrigida]


def identificadores_dos_avisos(avisos: list[Aviso]) -> list[str]:
    return sem_repeticao([aviso.ghsa for aviso in avisos])


def porque_da_biblioteca(avisos: list[Aviso], nota: float | None, prioridade: Prioridade) -> str:
    identificadores = identificadores_dos_avisos(avisos)
    if len(identificadores) == 1:
        falhas = "1 falha conhecida"
    else:
        falhas = f"{len(identificadores)} falhas conhecidas"
    return f"{falhas} ({', '.join(identificadores)}). {escrever_nota_da_acao(nota, prioridade)}."


def escrever_nota_da_acao(nota: float | None, prioridade: Prioridade) -> str:
    if nota is None:
        return f"Sem nota, falta CVSS ({ROTULO_DA_PRIORIDADE[prioridade]})"
    return f"Nota {escrever_nota(nota)} ({ROTULO_DA_PRIORIDADE[prioridade]})"


def impacto_da_biblioteca(avisos: list[Aviso], explicacao: Explicacao | None) -> str:
    if explicacao is not None:
        return explicacao.impacto
    return avisos[0].resumo


def teste_sugerido_pela_ia(explicacao: Explicacao | None) -> str | None:
    if explicacao is None or not tem_teste_sugerido_pela_ia(explicacao):
        return None
    return explicacao.teste_verificacao


def tem_teste_sugerido_pela_ia(explicacao: Explicacao) -> bool:
    return explicacao.gerada_por_ia and bool(explicacao.teste_verificacao)
