let paginaOriginal: string | null = null;

function htmlDaPagina(documento: Document): string {
  return `<!doctype html>\n${documento.documentElement.outerHTML}`;
}

export function guardarPaginaOriginal(documento: Document): void {
  paginaOriginal = htmlDaPagina(documento);
}

export function lerPaginaOriginal(): string {
  return paginaOriginal ?? htmlDaPagina(document);
}
