from rastro.configuracao.falhas_nos_cabecalhos import (
    cabecalho_que_mostra_versao,
    csp_tem_frame_ancestors,
    expoe_versao_do_servidor,
    ler_cabecalho,
    sem_csp,
    sem_hsts,
    sem_nosniff,
    sem_protecao_contra_frame,
)
from rastro.har.modelos import Requisicao


def pagina(cabecalhos: dict[str, str]) -> Requisicao:
    return Requisicao(
        indice=0,
        url="https://loja.exemplo/",
        metodo="GET",
        status=200,
        tipo_conteudo="text/html",
        cabecalhos_resposta=cabecalhos,
        cookies_resposta=[],
        conteudo=None,
    )


def test_ler_cabecalho_tira_espacos_e_devolve_vazio_quando_falta() -> None:
    assert ler_cabecalho(pagina({"server": "  nginx "}), "server") == "nginx"
    assert ler_cabecalho(pagina({}), "server") == ""


def test_r06_1_sem_csp_quando_o_cabecalho_falta_ou_esta_vazio() -> None:
    assert sem_csp(pagina({})) is True
    assert sem_csp(pagina({"content-security-policy": " "})) is True
    assert sem_csp(pagina({"content-security-policy": "default-src 'self'"})) is False


def test_r06_2_sem_hsts_quando_o_cabecalho_falta() -> None:
    assert sem_hsts(pagina({})) is True
    assert sem_hsts(pagina({"strict-transport-security": "max-age=1"})) is False


def test_r06_3_sem_nosniff_aceita_maiusculas_e_recusa_outro_valor() -> None:
    assert sem_nosniff(pagina({"x-content-type-options": "NOSNIFF"})) is False
    assert sem_nosniff(pagina({"x-content-type-options": "sniff"})) is True


def test_r06_4_frame_ancestors_so_conta_como_nome_de_diretiva() -> None:
    com_diretiva = pagina({"content-security-policy": "default-src 'self'; frame-ancestors 'none'"})
    no_valor = pagina({"content-security-policy": "default-src frame-ancestors"})

    assert csp_tem_frame_ancestors(com_diretiva) is True
    assert csp_tem_frame_ancestors(no_valor) is False


def test_r06_4_x_frame_options_ou_frame_ancestors_protegem_contra_frame() -> None:
    assert sem_protecao_contra_frame(pagina({})) is True
    assert sem_protecao_contra_frame(pagina({"x-frame-options": "DENY"})) is False
    politica = {"content-security-policy": "frame-ancestors 'self'"}
    assert sem_protecao_contra_frame(pagina(politica)) is False


def test_r06_5_cabecalho_que_mostra_versao_devolve_nome_e_valor() -> None:
    cabecalhos = {"server": "nginx", "x-powered-by": "PHP/8.1"}

    assert cabecalho_que_mostra_versao(pagina(cabecalhos)) == "x-powered-by: PHP/8.1"
    assert expoe_versao_do_servidor(pagina(cabecalhos)) is True


def test_r06_5_servidor_sem_numero_de_versao_nao_expoe() -> None:
    assert cabecalho_que_mostra_versao(pagina({"server": "nginx"})) is None
    assert expoe_versao_do_servidor(pagina({"server": "nginx"})) is False
