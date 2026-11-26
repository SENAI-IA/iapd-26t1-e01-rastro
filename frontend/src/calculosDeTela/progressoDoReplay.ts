import type { PassoDaVisita } from "../relatorio/tiposDoRelatorio.ts";

const REPLAY_MAIS_CURTO_MS = 5000;
const REPLAY_MAIS_LONGO_MS = 9000;
const REPLAY_POR_REQUISICAO_MS = 100;

export function duracaoDoReplay(requisicoes: number): number {
  return Math.min(REPLAY_MAIS_LONGO_MS, Math.max(REPLAY_MAIS_CURTO_MS, requisicoes * REPLAY_POR_REQUISICAO_MS));
}

export function progressoDoReplay(tempo: number, duracao: number, requisicoes: number): number {
  return (tempo / duracao) * requisicoes;
}

export function requisicoesQueChegaram(progresso: number, requisicoes: number): number {
  return Math.min(requisicoes, Math.ceil(progresso));
}

export function duracaoDaVisita(passos: PassoDaVisita[]): number {
  return Math.max(...passos.map((passo) => passo.inicio_ms + passo.duracao_ms));
}
