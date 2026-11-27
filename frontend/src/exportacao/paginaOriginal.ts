let paginaOriginal: string | null = null;

function htmlDaPagina(documento: Document): string {
  return `<!doctype html>\n${documento.documentElement.outerHTML}`;
}

export function guardarPaginaOriginal(documento: Document): void {
  paginaOriginal = htmlDaPagina(documento);
}

const DADOS_DO_RELATORIO = /(<script id="dados" type="application\/json">)[\s\S]*?(<\/script>)/;

export function lerPaginaOriginal(): string {
  return paginaOriginal ?? htmlDaPagina(document);
}

export function lerPaginaSemOsDados(): string {
  return lerPaginaOriginal().replace(DADOS_DO_RELATORIO, "$1$2");
}
