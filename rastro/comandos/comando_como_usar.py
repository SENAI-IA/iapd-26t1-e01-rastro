from rastro.comandos.navegador import abrir_no_navegador
from rastro.relatorio.html import caminho_do_modelo

TEXTO_COMO_USAR_ABERTO = 'Guia "Como usar" aberto no navegador: {caminho}'
TEXTO_COMO_USAR_SEM_NAVEGADOR = (
    "Não foi possível abrir o navegador. Abra este arquivo nele para ver o guia "
    '"Como usar": {caminho}'
)


def abrir_como_usar() -> int:
    caminho = caminho_do_modelo()
    if abrir_no_navegador(caminho):
        print(TEXTO_COMO_USAR_ABERTO.format(caminho=caminho))
    else:
        print(TEXTO_COMO_USAR_SEM_NAVEGADOR.format(caminho=caminho))
    return 0
