import type { Biblioteca, PassoDaVisita, Prioridade } from "../relatorio/tiposDoRelatorio.ts";

export interface ChegadaDeBiblioteca {
  id: string;
  pacote: string;
  versao: string;
  prioridade: Prioridade;
  inicio_ms: number;
  ordemDaRequisicao: number;
}

function chegadaComFalha(id: string, passo: PassoDaVisita, ordemDaRequisicao: number, bibliotecas: Biblioteca[]): ChegadaDeBiblioteca[] {
  const biblioteca = bibliotecas.find((candidata) => candidata.id === id);
  if (!biblioteca?.prioridade) {
    return [];
  }
  return [
    {
      id,
      pacote: biblioteca.pacote,
      versao: biblioteca.versao,
      prioridade: biblioteca.prioridade,
      inicio_ms: passo.inicio_ms,
      ordemDaRequisicao,
    },
  ];
}

function chegadasDoPasso(passo: PassoDaVisita, ordemDaRequisicao: number, bibliotecas: Biblioteca[]): ChegadaDeBiblioteca[] {
  return passo.bibliotecas.flatMap((id) => chegadaComFalha(id, passo, ordemDaRequisicao, bibliotecas));
}

function chegadaEAPrimeiraDaBiblioteca(chegada: ChegadaDeBiblioteca, posicao: number, todas: ChegadaDeBiblioteca[]): boolean {
  return todas.findIndex((outra) => outra.id === chegada.id) === posicao;
}

export function listarChegadas(passos: PassoDaVisita[], bibliotecas: Biblioteca[]): ChegadaDeBiblioteca[] {
  const todasAsChegadas = passos.flatMap((passo, ordemDaRequisicao) => chegadasDoPasso(passo, ordemDaRequisicao, bibliotecas));
  return todasAsChegadas.filter(chegadaEAPrimeiraDaBiblioteca);
}
