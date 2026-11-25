from rastro import atalho
from rastro.comandos.saida_de_erro import encerrar_com_erro

TEXTO_INSTALADO = "Pronto! Comando rastro instalado."
TEXTO_TESTE_NO_MESMO_TERMINAL = "Teste com: rastro --help"
TEXTO_TESTE_NUM_TERMINAL_NOVO = "Abra um terminal novo e teste com: rastro --help"


def instalar_comando() -> int:
    try:
        instalacao = atalho.instalar()
    except (atalho.ProjetoNaoEncontrado, atalho.AtalhoDeOutro) as erro:
        return encerrar_com_erro(str(erro))
    print(TEXTO_INSTALADO)
    if instalacao.path_alterado_em:
        print(TEXTO_TESTE_NUM_TERMINAL_NOVO)
    else:
        print(TEXTO_TESTE_NO_MESMO_TERMINAL)
    return 0
