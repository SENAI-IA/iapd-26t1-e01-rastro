import type { Camada, PassoDaVisita } from "../relatorio/tiposDoRelatorio.ts";
import type { ChegadaDeBiblioteca } from "./chegadasDaVisita.ts";
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
  rotulos: Rotulo<ChegadaDeBiblioteca>[];
  ladosComRotulo: Set<Lado>;
}

function pontoDaOrdem(passos: PassoDaVisita[], ordem: number): Ponto {
  const passo = passos[ordem];
  return pontoNoCirculo(raioComEspalhamento(passo.camada, passo.indice_requisicao), anguloDaOrdem(ordem, passos.length));
}

function comPonto(passos: PassoDaVisita[], ordens: number[]): PontoDaRequisicao[] {
  return ordens.map((ordem) => ({ ordem, ponto: pontoDaOrdem(passos, ordem) }));
}

function estaEmAlerta(comFalha: number[], requisicoesTocadas: number): boolean {
  const ultimaFalha = comFalha.at(-1);
  return ultimaFalha !== undefined && requisicoesTocadas - ultimaFalha < ALERTA_DEPOIS_DA_FALHA;
}

function rotulosQueChegaram(passos: PassoDaVisita[], chegadas: ChegadaDeBiblioteca[], requisicoesTocadas: number): Rotulo<ChegadaDeBiblioteca>[] {
  const queChegaram = chegadas.filter((chegada) => chegada.ordemDaRequisicao < requisicoesTocadas);
  return posicionarRotulos(queChegaram.map((chegada) => ({ item: chegada, ancora: pontoDaOrdem(passos, chegada.ordemDaRequisicao) })));
}

export function estadoDoRadar(passos: PassoDaVisita[], chegadas: ChegadaDeBiblioteca[], requisicoesTocadas: number): EstadoDoRadar {
  const total = passos.length;
  const chegaram = [...passos.keys()].filter((ordem) => ordem < requisicoesTocadas);
  const comFalha = chegaram.filter((ordem) => passos[ordem].prioridade !== null);
  const terminou = requisicoesTocadas >= total;
  const recentes = terminou ? [] : chegaram.filter((ordem) => requisicoesTocadas - ordem < RASTRO_RECENTE);
  const anguloAtual = anguloDaOrdem(Math.min(requisicoesTocadas, total), total);
  const repetidas = comFalha.filter((ordem) => !chegadas.some((chegada) => chegada.ordemDaRequisicao === ordem));
  return {
    terminou,
    emAlerta: estaEmAlerta(comFalha, requisicoesTocadas),
    temFalha: comFalha.length > 0,
    camadasComFalha: new Set(comFalha.map((ordem) => passos[ordem].camada)),
    anguloAtual,
    ponteiro: pontoNoCirculo(RAIO_EXTERNO, anguloAtual),
    momento: chegaram.length > 0 ? passos[chegaram.length - 1].inicio_ms : 0,
    chegaram: comPonto(passos, chegaram),
    recentes: comPonto(passos, recentes),
    falhasRepetidas: comPonto(passos, repetidas),
    rotulos: rotulosQueChegaram(passos, chegadas, requisicoesTocadas),
    ladosComRotulo: new Set(chegadas.map((chegada) => ladoDoPonto(pontoDaOrdem(passos, chegada.ordemDaRequisicao)))),
  };
}
