import os
from collections.abc import Callable
from pathlib import Path

from rastro.comandos.argumentos import AJUDA_SEM_IA
from rastro.comandos.resumo_no_terminal import AVISO_SEM_IA, mostrar_resultado
from rastro.comandos.saida_de_erro import encerrar_com_erro
from rastro.fluxo_da_analise import analisar
from rastro.fontes.github_advisory import GitHubAdvisory
from rastro.fontes.nvd import Nvd
from rastro.fontes.osv import Osv
from rastro.fontes.registro_npm import RegistroNpm
from rastro.har.leitor_do_har import ErroAoLerHar
from rastro.ia.cliente import ClienteDeIA
from rastro.ia.escolha_da_ia import (
    VARIAVEL_DA_IA,
    CLIDaIAAusente,
    IAInvalida,
    escolher_ia,
    localizar_cli,
)
from rastro.ia.provedor import ProvedorDeIA
from rastro.ia.provedores.claude import ProvedorClaude
from rastro.ia.provedores.codex import ProvedorCodex
from rastro.ia.provedores.kiro import ProvedorKiro
from rastro.pentest.erros import ErroNoPentest
from rastro.pentest.execucao_do_pentest import carregar_resultado_do_pentest
from rastro.relatorio.gravacao_do_relatorio import (
    RelatorioJaExiste,
    caminho_do_relatorio,
    gravar_relatorio,
    nome_da_aplicacao,
    pasta_padrao,
)
from rastro.relatorio.limitacoes_da_analise import (
    TEXTO_ACHADOS_SEM_EXPLICACAO,
    TEXTO_CONTINUA_IGUAL_SEM_IA,
)
from rastro.relatorio.montagem_do_relatorio import montar_relatorio
from rastro.terminal import AndamentoNoTerminal, LinhaAoVivo

SUGESTAO_SEM_IA = f"Use --sem-ia ({AJUDA_SEM_IA})."
AVISO_COM_IA = (
    "Análise com a IA {ia}. Cada chamada à IA pode levar até 2 minutos; "
    "o que ela sugere passa pelas travas antes do relatório."
)
PROVEDORES_DAS_IAS: dict[str, Callable[[str], ProvedorDeIA]] = {
    "kiro": ProvedorKiro,
    "claude": ProvedorClaude,
    "codex": ProvedorCodex,
}


def analisar_com_ia(
    caminho_har: Path,
    saida: Path | None,
    opcao_da_ia: str | None,
    abrir: bool,
    caminho_pentest: Path | None,
) -> int:
    try:
        ia = montar_cliente_de_ia(opcao_da_ia)
    except IAInvalida as erro:
        return encerrar_com_erro(str(erro))
    except CLIDaIAAusente as erro:
        return encerrar_com_erro(f"{erro}. Escolha outra IA com --ia. {SUGESTAO_SEM_IA}")
    avisar_analise_com_ia(ia)
    return analisar_e_gravar(caminho_har, saida, ia, abrir, caminho_pentest)


def montar_cliente_de_ia(opcao_da_ia: str | None) -> ClienteDeIA:
    nome_da_ia = escolher_ia(opcao_da_ia, os.environ.get(VARIAVEL_DA_IA))
    executavel = localizar_cli(nome_da_ia)
    return ClienteDeIA(PROVEDORES_DAS_IAS[nome_da_ia](executavel))


def analisar_sem_ia(
    caminho_har: Path, saida: Path | None, abrir: bool, caminho_pentest: Path | None
) -> int:
    avisar_analise_sem_ia()
    return analisar_e_gravar(caminho_har, saida, None, abrir, caminho_pentest)


def analisar_e_gravar(
    caminho_har: Path,
    saida: Path | None,
    ia: ClienteDeIA | None,
    abrir: bool,
    caminho_pentest: Path | None = None,
    gravado_pelo_rastro: bool = False,
) -> int:
    try:
        pentest = (
            carregar_resultado_do_pentest(caminho_pentest, caminho_har) if caminho_pentest else None
        )
        with LinhaAoVivo() as linha:
            andamento = AndamentoNoTerminal(linha)
            analise = analisar(
                caminho_har,
                GitHubAdvisory(),
                RegistroNpm(),
                ia,
                Osv(),
                Nvd(),
                gravado_pelo_rastro=gravado_pelo_rastro,
                andamento=andamento,
            )
            andamento.terminar()
    except (ErroAoLerHar, ErroNoPentest) as erro:
        return encerrar_com_erro(str(erro))
    relatorio = montar_relatorio(analise, pentest)
    aplicacao = nome_da_aplicacao(analise.site, caminho_har)
    pasta = caminho_do_relatorio(saida or pasta_padrao(), aplicacao, analise.inicio)
    try:
        gravado = gravar_relatorio(pasta, relatorio)
    except RelatorioJaExiste as erro:
        return encerrar_com_erro(str(erro))
    mostrar_resultado(pasta, gravado, relatorio, abrir)
    return 0


def avisar_analise_com_ia(ia: ClienteDeIA) -> None:
    print(AVISO_COM_IA.format(ia=ia.provedor.nome))
    print()


def avisar_analise_sem_ia() -> None:
    print(AVISO_SEM_IA)
    print(TEXTO_ACHADOS_SEM_EXPLICACAO)
    print(TEXTO_CONTINUA_IGUAL_SEM_IA)
    print()
