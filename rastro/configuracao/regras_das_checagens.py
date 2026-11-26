from rastro.configuracao.modelos import RegraDeChecagem

CSP_AUSENTE = RegraDeChecagem("C01", "CSP ausente", "media", "infra")
HSTS_AUSENTE = RegraDeChecagem("C02", "HSTS ausente", "media", "infra")
NOSNIFF_AUSENTE = RegraDeChecagem("C03", "nosniff ausente", "baixa", "infra")
FRAME_SEM_PROTECAO = RegraDeChecagem("C04", "proteção contra frame ausente", "baixa", "infra")
SERVIDOR_EXPOE_VERSAO = RegraDeChecagem("C05", "servidor expõe versão", "baixa", "infra")
COOKIE_SEM_HTTPONLY = RegraDeChecagem("C06", "cookie sem HttpOnly", "media", "dev back-end")
COOKIE_SEM_SECURE = RegraDeChecagem("C07", "cookie sem Secure", "media", "dev back-end")
COOKIE_SEM_SAMESITE = RegraDeChecagem("C08", "cookie sem SameSite", "baixa", "dev back-end")

MOTIVO_SEM_PAGINAS_HTML = "nenhuma resposta HTML do site analisado no HAR"
MOTIVO_SEM_COOKIES = (
    "o HAR não traz cookies do site analisado (ex.: exportado no modo sanitized); "
    "exportar o HAR completo inclui as checagens de cookie C06 a C08"
)
MOTIVO_SEM_COOKIES_NA_GRAVACAO = (
    "o site não criou nenhum cookie durante a visita gravada pelo Rastro; "
    "a gravação guarda os cookies, então não há o que conferir"
)

IDS_DAS_CHECAGENS_DE_COOKIE = (COOKIE_SEM_HTTPONLY.id, COOKIE_SEM_SECURE.id, COOKIE_SEM_SAMESITE.id)
