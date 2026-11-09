import type { Biblioteca, PassoDaVisita, Prioridade } from "../tipos.ts";

export interface Chegada {
  id: string;
  pacote: string;
  versao: string;
  prioridade: Prioridade;
  inicio_ms: number;
  ordem: number;
}

export function listarChegadas(passos: PassoDaVisita[], bibliotecas: Biblioteca[]): Chegada[] {
  const chegadas = new Map<string, Chegada>();
  for (const [ordem, passo] of passos.entries()) {
    for (const id of passo.bibliotecas) {
      const biblioteca = bibliotecas.find((candidata) => candidata.id === id);
      if (!chegadas.has(id) && biblioteca?.prioridade) {
        chegadas.set(id, {
          id,
          pacote: biblioteca.pacote,
          versao: biblioteca.versao,
          prioridade: biblioteca.prioridade,
          inicio_ms: passo.inicio_ms,
          ordem,
        });
      }
    }
  }
  return [...chegadas.values()];
}
