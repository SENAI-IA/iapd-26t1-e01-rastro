import type { LinhaDaSimulacao, TomDaSaida } from "../conteudo/simulacoesDoGuia.ts";

export type TomNaTela = TomDaSaida | "prompt" | "pergunta" | "resposta";

export interface PedacoDaLinha {
  texto: string;
  tom?: TomNaTela;
}

export interface LinhaNaTela {
  pedacos: PedacoDaLinha[];
  cursor?: boolean;
}

export interface QuadroDoTerminal {
  esperaAntes: number;
  tela: LinhaNaTela[];
}

const GIRO = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏";
const MARCA_DE_FEITO = "✓ ";
const PROMPT = "$ ";
const DIGITAR_UMA_LETRA_MS = 26;
const ANTES_DE_DIGITAR_MS = 400;
const DEPOIS_DO_COMANDO_MS = 300;
const UM_GIRO_MS = 80;
const ETAPA_PADRAO_MS = 1000;
const ANTES_DA_RESPOSTA_MS = 900;
const DEPOIS_DA_RESPOSTA_MS = 300;
const LINHA_PADRAO_MS = 260;
const SEGUNDOS_POR_MINUTO = 60;

interface Roteiro {
  fixas: LinhaNaTela[];
  quadros: QuadroDoTerminal[];
}

function mostrar(roteiro: Roteiro, esperaAntes: number, atual: LinhaNaTela | null = null): void {
  const tela = atual === null ? [...roteiro.fixas] : [...roteiro.fixas, atual];
  roteiro.quadros.push({ esperaAntes, tela });
}

function fixar(roteiro: Roteiro, linha: LinhaNaTela, esperaAntes: number): void {
  roteiro.fixas = [...roteiro.fixas, linha];
  mostrar(roteiro, esperaAntes);
}

function segundosDoTempo(tempo: string): number {
  const [minutos, segundos] = tempo.split(":").map(Number);
  return minutos * SEGUNDOS_POR_MINUTO + segundos;
}

function escreverRelogio(segundos: number): string {
  const minutos = Math.floor(segundos / SEGUNDOS_POR_MINUTO);
  return `${minutos}:${String(segundos % SEGUNDOS_POR_MINUTO).padStart(2, "0")}`;
}

function linhaDoComando(digitado: string, cursor: boolean): LinhaNaTela {
  return { pedacos: [{ texto: PROMPT, tom: "prompt" }, { texto: digitado, tom: "forte" }], cursor };
}

function linhaDaEtapaFeita(etapa: string, tempo: string): LinhaNaTela {
  return { pedacos: [{ texto: MARCA_DE_FEITO, tom: "bom" }, { texto: `${etapa} · ${tempo}` }] };
}

function digitarComando(roteiro: Roteiro, comando: string): void {
  mostrar(roteiro, 0, linhaDoComando("", true));
  [...comando].forEach((_letra, indice) => {
    const espera = indice === 0 ? ANTES_DE_DIGITAR_MS : DIGITAR_UMA_LETRA_MS;
    mostrar(roteiro, espera, linhaDoComando(comando.slice(0, indice + 1), true));
  });
  fixar(roteiro, linhaDoComando(comando, false), DEPOIS_DO_COMANDO_MS);
}

function girarEtapa(roteiro: Roteiro, etapa: string, tempo: string, espera: number): void {
  const giros = Math.max(1, Math.round(espera / UM_GIRO_MS));
  const segundosFinais = segundosDoTempo(tempo);
  for (let giro = 0; giro < giros; giro += 1) {
    const relogio = escreverRelogio(Math.floor((segundosFinais * giro) / giros));
    const texto = `${GIRO[giro % GIRO.length]} ${etapa} · ${relogio}`;
    mostrar(roteiro, giro === 0 ? 0 : UM_GIRO_MS, { pedacos: [{ texto, tom: "fraco" }] });
  }
  fixar(roteiro, linhaDaEtapaFeita(etapa, tempo), UM_GIRO_MS);
}

function responderPergunta(roteiro: Roteiro, pergunta: string, resposta: string): void {
  const linhaDaPergunta = (respondido: string): LinhaNaTela => ({
    pedacos: [{ texto: pergunta, tom: "pergunta" }, { texto: respondido, tom: "resposta" }],
    cursor: respondido === "",
  });
  mostrar(roteiro, 0, linhaDaPergunta(""));
  fixar(roteiro, linhaDaPergunta(resposta), ANTES_DA_RESPOSTA_MS);
  mostrar(roteiro, DEPOIS_DA_RESPOSTA_MS);
}

function tocarLinha(roteiro: Roteiro, linha: LinhaDaSimulacao): void {
  if ("comando" in linha) {
    digitarComando(roteiro, linha.comando);
    return;
  }
  if ("etapa" in linha) {
    girarEtapa(roteiro, linha.etapa, linha.tempo, linha.espera ?? ETAPA_PADRAO_MS);
    return;
  }
  if ("pergunta" in linha) {
    responderPergunta(roteiro, linha.pergunta, linha.resposta);
    return;
  }
  fixar(roteiro, { pedacos: [{ texto: linha.saida, tom: linha.tom }] }, LINHA_PADRAO_MS);
  if (linha.espera !== undefined) {
    mostrar(roteiro, linha.espera);
  }
}

export function quadrosDoTerminal(linhas: LinhaDaSimulacao[]): QuadroDoTerminal[] {
  const roteiro: Roteiro = { fixas: [], quadros: [{ esperaAntes: 0, tela: [] }] };
  linhas.forEach((linha) => tocarLinha(roteiro, linha));
  fixar(roteiro, linhaDoComando("", true), LINHA_PADRAO_MS);
  return roteiro.quadros;
}

function linhaParada(linha: LinhaDaSimulacao): LinhaNaTela {
  if ("comando" in linha) {
    return linhaDoComando(linha.comando, false);
  }
  if ("etapa" in linha) {
    return linhaDaEtapaFeita(linha.etapa, linha.tempo);
  }
  if ("pergunta" in linha) {
    return { pedacos: [{ texto: linha.pergunta, tom: "pergunta" }, { texto: linha.resposta, tom: "resposta" }] };
  }
  return { pedacos: [{ texto: linha.saida, tom: linha.tom }] };
}

export function telaParada(linhas: LinhaDaSimulacao[]): LinhaNaTela[] {
  return [...linhas.map(linhaParada), linhaDoComando("", true)];
}
