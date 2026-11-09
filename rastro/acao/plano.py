from rastro.acao.modelos import Acao, CorrecaoDaChecagem
from rastro.configuracao.modelos import Checagem
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.conector import Aviso
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado, Prioridade
from rastro.risco.nota import escrever_nota
from rastro.risco.prioridade import classificar_prioridade, nota_da_biblioteca, ordenar_achados
from rastro.travas.faixa_de_versao import ler_versao

QUEM_RESOLVE_A_BIBLIOTECA = "dev front-end"
SEM_CORRECAO_PUBLICADA = "sem correção publicada: avaliar troca ou mitigação"

ORDEM_DA_PRIORIDADE: dict[Prioridade, int] = {"alta": 0, "media": 1, "baixa": 2, "a avaliar": 3}
ROTULO_DA_PRIORIDADE: dict[Prioridade, str] = {
    "alta": "alta",
    "media": "média",
    "baixa": "baixa",
    "a avaliar": "a avaliar",
}

CORRECOES_DAS_CHECAGENS = {
    "C01": CorrecaoDaChecagem(
        "Enviar o cabeçalho Content-Security-Policy nas páginas HTML do site",
        "Sem CSP, um script injetado (XSS) roda sem barreira no navegador de quem acessa.",
    ),
    "C02": CorrecaoDaChecagem(
        "Enviar o cabeçalho Strict-Transport-Security nas respostas em HTTPS",
        "Sem HSTS, a próxima visita pode cair para HTTP e ser interceptada.",
    ),
    "C03": CorrecaoDaChecagem(
        "Enviar o cabeçalho X-Content-Type-Options: nosniff nas páginas HTML do site",
        "Sem nosniff, o navegador pode tratar como script um arquivo que não é script.",
    ),
    "C04": CorrecaoDaChecagem(
        "Enviar X-Frame-Options ou a diretiva frame-ancestors na CSP",
        "Sem essa proteção, outro site pode abrir este dentro de um frame e induzir cliques"
        " (clickjacking).",
    ),
    "C05": CorrecaoDaChecagem(
        "Tirar a versão dos cabeçalhos Server e X-Powered-By",
        "A versão exposta facilita procurar falhas conhecidas do servidor.",
    ),
    "C06": CorrecaoDaChecagem(
        "Marcar os cookies do site como HttpOnly",
        "Sem HttpOnly, um script injetado (XSS) consegue ler o cookie e roubar a sessão.",
    ),
    "C07": CorrecaoDaChecagem(
        "Marcar os cookies do site como Secure",
        "Sem Secure, o cookie pode ir por HTTP e ser interceptado.",
    ),
    "C08": CorrecaoDaChecagem(
        "Definir o atributo SameSite nos cookies do site",
        "Sem SameSite definido, o cookie fica mais exposto a requisições forjadas por outros"
        " sites (CSRF).",
    ),
}


def montar_plano_de_acao(
    achados: list[Achado],
    explicacoes: dict[str, Explicacao],
    checagens: list[Checagem],
) -> list[Acao]:
    acoes = acoes_das_bibliotecas(achados, explicacoes) + acoes_das_checagens(checagens)
    return ordenar_acoes(acoes)


def chave_da_biblioteca(biblioteca: Biblioteca) -> str:
    return f"{biblioteca.pacote}@{biblioteca.versao}"


def acoes_das_bibliotecas(achados: list[Achado], explicacoes: dict[str, Explicacao]) -> list[Acao]:
    acoes = []
    for chave, achados_da_biblioteca in agrupar_por_biblioteca(achados).items():
        acoes.append(acao_da_biblioteca(chave, achados_da_biblioteca, explicacoes.get(chave)))
    return acoes


def agrupar_por_biblioteca(achados: list[Achado]) -> dict[str, list[Achado]]:
    grupos: dict[str, list[Achado]] = {}
    for achado in achados:
        if achado.biblioteca.situacao != "confirmada":
            continue
        grupos.setdefault(chave_da_biblioteca(achado.biblioteca), []).append(achado)
    return grupos


def acao_da_biblioteca(
    chave: str, achados_da_biblioteca: list[Achado], explicacao: Explicacao | None
) -> Acao:
    achados_em_ordem = ordenar_achados(achados_da_biblioteca)
    biblioteca = achados_em_ordem[0].biblioteca
    avisos = [achado.aviso for achado in achados_em_ordem]
    nota = nota_da_biblioteca(achados_em_ordem)
    prioridade = classificar_prioridade(nota)
    return Acao(
        id=chave,
        prioridade=prioridade,
        nota=nota,
        o_que_fazer=o_que_fazer_na_biblioteca(biblioteca, avisos),
        porque=porque_da_biblioteca(avisos, nota, prioridade),
        impacto=impacto_da_biblioteca(avisos, explicacao),
        quem_resolve=QUEM_RESOLVE_A_BIBLIOTECA,
        refs=ids_dos_avisos(avisos),
    )


def o_que_fazer_na_biblioteca(biblioteca: Biblioteca, avisos: list[Aviso]) -> str:
    versao_alvo = menor_versao_que_corrige_todos(avisos)
    sem_correcao = ids_dos_avisos(avisos_sem_correcao(avisos))
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
    return max(versoes_corrigidas, key=ler_versao)


def avisos_sem_correcao(avisos: list[Aviso]) -> list[Aviso]:
    return [aviso for aviso in avisos if not aviso.versao_corrigida]


def ids_dos_avisos(avisos: list[Aviso]) -> list[str]:
    return list(dict.fromkeys(aviso.ghsa for aviso in avisos))


def porque_da_biblioteca(avisos: list[Aviso], nota: float | None, prioridade: Prioridade) -> str:
    ids = ids_dos_avisos(avisos)
    falhas = "1 falha conhecida" if len(ids) == 1 else f"{len(ids)} falhas conhecidas"
    return f"{falhas} ({', '.join(ids)}). {escrever_nota_da_acao(nota, prioridade)}."


def escrever_nota_da_acao(nota: float | None, prioridade: Prioridade) -> str:
    if nota is None:
        return f"Sem nota, falta CVSS ({ROTULO_DA_PRIORIDADE[prioridade]})"
    return f"Nota {escrever_nota(nota)} ({ROTULO_DA_PRIORIDADE[prioridade]})"


def impacto_da_biblioteca(avisos: list[Aviso], explicacao: Explicacao | None) -> str:
    if explicacao is not None:
        return explicacao.impacto
    return avisos[0].resumo


def acoes_das_checagens(checagens: list[Checagem]) -> list[Acao]:
    return [acao_da_checagem(checagem) for checagem in checagens if checagem.situacao == "falhou"]


def acao_da_checagem(checagem: Checagem) -> Acao:
    correcao = CORRECOES_DAS_CHECAGENS[checagem.id]
    return Acao(
        id=checagem.id,
        prioridade=checagem.severidade,
        nota=None,
        o_que_fazer=correcao.o_que_fazer,
        porque=porque_da_checagem(checagem),
        impacto=correcao.impacto,
        quem_resolve=checagem.quem_resolve,
        refs=[checagem.id],
    )


def porque_da_checagem(checagem: Checagem) -> str:
    severidade = ROTULO_DA_PRIORIDADE[checagem.severidade]
    return f"Regra {checagem.id} ({checagem.titulo}), severidade {severidade}: {checagem.detalhe}"


def ordenar_acoes(acoes: list[Acao]) -> list[Acao]:
    return sorted(acoes, key=chave_da_ordem_da_acao)


def chave_da_ordem_da_acao(acao: Acao) -> tuple[int, bool, float]:
    sem_nota = acao.nota is None
    nota_decrescente = -acao.nota if acao.nota is not None else 0.0
    return (ORDEM_DA_PRIORIDADE[acao.prioridade], sem_nota, nota_decrescente)
