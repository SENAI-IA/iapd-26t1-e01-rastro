import sys

from rastro.comandos.saida_de_erro import encerrar_com_erro
from rastro.instalacao import instalador, sobras
from rastro.instalacao.atalho import AtalhoDeOutro
from rastro.instalacao.sobras import Sobra, comando_para_apagar

TEXTO_DESINSTALADO = "Comando rastro removido."
TEXTO_NADA_A_REMOVER = "O comando rastro não está instalado."
TEXTO_PARA_LIMPAR_TUDO = "Para limpar tudo, apague também:"


def desinstalar_comando() -> int:
    try:
        desinstalacao = instalador.desinstalar()
    except AtalhoDeOutro as erro:
        return encerrar_com_erro(str(erro))
    if desinstalacao.atalho_removido is None and not desinstalacao.path_removido_de:
        print(TEXTO_NADA_A_REMOVER)
    else:
        print(TEXTO_DESINSTALADO)
    mostrar_como_limpar_tudo(sobras.sobras())
    return 0


def mostrar_como_limpar_tudo(sobras_encontradas: list[Sobra]) -> None:
    if not sobras_encontradas:
        return
    print(TEXTO_PARA_LIMPAR_TUDO)
    no_windows = sys.platform == "win32"
    for sobra in sobras_encontradas:
        print(f"  {sobra.descricao}: {comando_para_apagar(sobra.caminho, no_windows)}")
