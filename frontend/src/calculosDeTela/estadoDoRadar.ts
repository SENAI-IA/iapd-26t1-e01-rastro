import type { Camada, PassoDaVisita } from "../relatorio/tiposDoRelatorio.ts";
import type { Chegada } from "./chegadasDaVisita.ts";
import {
  anguloDaOrdem,
  ladoDoPonto,
  pontoNoCirculo,
  posicionarRotulos,
  RAIO_EXTERNO,
  raioComEspalhamento,
  type Lado,
  type Ponto,
  type Rotulo,
} from "./geometriaDoRadar.ts";

const RASTRO_RECENTE = 4;
const ALERTA_DEPOIS_DA_FALHA = 6;

export interface PontoDaRequisicao {
  ordem: number;
  ponto: Ponto;
}

export interface EstadoDoRadar {
  terminou: boolean;
  emAlerta: boolean;
  temFalha: boolean;
  camadasComFalha: Set<Camada>;
  anguloAtual: number;
  ponteiro: Ponto;
  momento: number;
  chegaram: PontoDaRequisicao[];
  recentes: PontoDaRequisicao[];
  falhasRepetidas: PontoDaRequisicao[];
  rotulos: Rotulo<Chegada>[];
  ladosComRotulo: Set<Lado>;
}

function pontoDaOrdem(passos: PassoDaVisita[], ordem: number): Ponto {
  const passo = passos[ordem];
  return pontoNoCirculo(raioComEspalhamento(passo.camada, passo.indice_requisicao), anguloDaOrdem(ordem, passos.length));
}

function comPonto(passos: PassoDaVisita[], ordens: number[]): PontoDaRequisicao[] {
  return ordens.map((ordem) => ({ ordem, ponto: pontoDaOrdem(passos, ordem) }));
}

function estaEmAlerta(comFalha: number[], progresso: number): boolean {
  const ultimaFalha = comFalha.at(-1);
  return ultimaFalha !== undefined && progresso - ultimaFalha < ALERTA_DEPOIS_DA_FALHA;
}

function rotulosQueChegaram(passos: PassoDaVisita[], chegadas: Chegada[], progresso: number): Rotulo<Chegada>[] {
  const queChegaram = chegadas.filter((chegada) => chegada.ordem < progresso);
  return posicionarRotulos(queChegaram.map((chegada) => ({ item: chegada, ancora: pontoDaOrdem(passos, chegada.ordem) })));
}

export function estadoDoRadar(passos: PassoDaVisita[], chegadas: Chegada[], progresso: number): EstadoDoRadar {
  const total = passos.length;
  const chegaram = passos.map((_, ordem) => ordem).filter((ordem) => ordem < progresso);
  const comFalha = chegaram.filter((ordem) => passos[ordem].prioridade !== null);
  const terminou = progresso >= total;
  const recentes = terminou ? [] : chegaram.filter((ordem) => progresso - ordem < RASTRO_RECENTE);
  const anguloAtual = anguloDaOrdem(Math.min(progresso, total), total);
  const repetidas = comFalha.filter((ordem) => !chegadas.some((chegada) => chegada.ordem === ordem));
  return {
    terminou,
    emAlerta: estaEmAlerta(comFalha, progresso),
    temFalha: comFalha.length > 0,
    camadasComFalha: new Set(comFalha.map((ordem) => passos[ordem].camada)),
    anguloAtual,
    ponteiro: pontoNoCirculo(RAIO_EXTERNO, anguloAtual),
    momento: chegaram.length > 0 ? passos[chegaram.length - 1].inicio_ms : 0,
    chegaram: comPonto(passos, chegaram),
    recentes: comPonto(passos, recentes),
    falhasRepetidas: comPonto(passos, repetidas),
    rotulos: rotulosQueChegaram(passos, chegadas, progresso),
    ladosComRotulo: new Set(chegadas.map((chegada) => ladoDoPonto(pontoDaOrdem(passos, chegada.ordem)))),
  };
}
