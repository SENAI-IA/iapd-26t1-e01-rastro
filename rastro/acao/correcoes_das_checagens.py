from rastro.acao.modelos import CorrecaoDaChecagem

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
