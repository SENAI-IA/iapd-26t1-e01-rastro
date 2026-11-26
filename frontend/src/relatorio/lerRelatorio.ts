import type { Relatorio } from "./tiposDoRelatorio.ts";

export function lerRelatorio(documento: Document): Relatorio | null {
  const conteudo = documento.getElementById("dados")?.textContent?.trim();
  if (!conteudo) {
    return null;
  }
  try {
    return JSON.parse(conteudo) as Relatorio;
  } catch {
    return null;
  }
}
