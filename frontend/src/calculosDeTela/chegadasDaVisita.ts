import type { Biblioteca, PassoDaVisita, Prioridade } from "../relatorio/tiposDoRelatorio.ts";

export interface ChegadaDeBiblioteca {
  id: string;
  pacote: string;
  versao: string;
  prioridade: Prioridade;
  inicio_ms: number;
  ordemDaRequisicao: number;
}

export function listarChegadas(passos: PassoDaVisita[], bibliotecas: Biblioteca[]): ChegadaDeBiblioteca[] {
  const chegadas = new Map<string, ChegadaDeBiblioteca>();
  for (const [ordemDaRequisicao, passo] of passos.entries()) {
    for (const id of passo.bibliotecas) {
      const biblioteca = bibliotecas.find((candidata) => candidata.id === id);
      if (!chegadas.has(id) && biblioteca?.prioridade) {
        chegadas.set(id, {
          id,
          pacote: biblioteca.pacote,
          versao: biblioteca.versao,
          prioridade: biblioteca.prioridade,
          inicio_ms: passo.inicio_ms,
          ordemDaRequisicao,
        });
      }
    }
  }
  return [...chegadas.values()];
}
