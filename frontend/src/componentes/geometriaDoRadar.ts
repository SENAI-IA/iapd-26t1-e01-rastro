import type { Camada } from "../tipos.ts";

export const ALTURA = 440;
export const CENTRO = { x: 360, y: ALTURA / 2 };
export const RAIO_EXTERNO = 196;
export const RAIO_DA_CAMADA: Record<Camada, number> = {
  pagina: 52,
  script: 96,
  estilo: 128,
  dados: 158,
  midia: 186,
};

const ABERTURA_NO_TOPO = 44;
const DISTANCIA_DA_COLUNA_DE_ROTULOS = 222;
const ESPACO_ENTRE_ROTULOS = 27;
const MARGEM = 18;

export interface Ponto {
  x: number;
  y: number;
}

export type Lado = "direita" | "esquerda";

export interface Rotulo<T> {
  item: T;
  ancora: Ponto;
  lado: Lado;
  y: number;
  x: number;
}

const LARGURA_DA_COLUNA_DE_ROTULOS = 175;
const FOLGA_DO_DISCO = 14;

export function enquadramento(ladosComRotulo: Set<Lado>): string {
  const alcanceDoLado = (lado: Lado) =>
    ladosComRotulo.has(lado)
      ? DISTANCIA_DA_COLUNA_DE_ROTULOS + LARGURA_DA_COLUNA_DE_ROTULOS
      : RAIO_EXTERNO + FOLGA_DO_DISCO;
  const esquerda = CENTRO.x - alcanceDoLado("esquerda");
  const largura = alcanceDoLado("esquerda") + alcanceDoLado("direita");
  return `${esquerda} 0 ${largura} ${ALTURA}`;
}

export function ladoDoPonto(ponto: Ponto): Lado {
  return ponto.x >= CENTRO.x ? "direita" : "esquerda";
}

export function anguloDaOrdem(ordem: number, total: number): number {
  const fracao = total === 0 ? 0 : ordem / total;
  return -90 + ABERTURA_NO_TOPO / 2 + fracao * (360 - ABERTURA_NO_TOPO);
}

export function pontoNoCirculo(raio: number, angulo: number): Ponto {
  const radianos = (angulo * Math.PI) / 180;
  return { x: CENTRO.x + raio * Math.cos(radianos), y: CENTRO.y + raio * Math.sin(radianos) };
}

export function raioComEspalhamento(camada: Camada, indice: number): number {
  return RAIO_DA_CAMADA[camada] + ((indice % 3) - 1) * 6;
}

export function fatiaDoRastro(anguloFinal: number, abertura: number): string {
  const inicio = pontoNoCirculo(RAIO_EXTERNO, anguloFinal - abertura);
  const fim = pontoNoCirculo(RAIO_EXTERNO, anguloFinal);
  return `M${CENTRO.x},${CENTRO.y} L${inicio.x},${inicio.y} A${RAIO_EXTERNO},${RAIO_EXTERNO} 0 0 1 ${fim.x},${fim.y} Z`;
}

export function posicionarRotulos<T>(itens: { item: T; ancora: Ponto }[]): Rotulo<T>[] {
  const lados: Lado[] = ["direita", "esquerda"];
  return lados.flatMap((lado) => {
    const doLado = itens
      .filter(({ ancora }) => ladoDoPonto(ancora) === lado)
      .sort((a, b) => a.ancora.y - b.ancora.y);
    return empilharSemSobrepor(doLado).map(({ item, ancora }, posicao, todos) => ({
      item,
      ancora,
      lado,
      y: todos[posicao].y,
      x: CENTRO.x + (lado === "direita" ? 1 : -1) * DISTANCIA_DA_COLUNA_DE_ROTULOS,
    }));
  });
}

function empilharSemSobrepor<T>(itens: { item: T; ancora: Ponto }[]): { item: T; ancora: Ponto; y: number }[] {
  const empilhados: { item: T; ancora: Ponto; y: number }[] = [];
  for (const { item, ancora } of itens) {
    const anterior = empilhados.at(-1);
    const y = Math.max(ancora.y, MARGEM, anterior ? anterior.y + ESPACO_ENTRE_ROTULOS : -Infinity);
    empilhados.push({ item, ancora, y });
  }
  let limite = ALTURA - MARGEM;
  for (const rotulo of [...empilhados].reverse()) {
    rotulo.y = Math.min(rotulo.y, limite);
    limite = rotulo.y - ESPACO_ENTRE_ROTULOS;
  }
  return empilhados;
}

export function caminhoDoFio(ancora: Ponto, rotulo: { x: number; y: number; lado: Lado }): string {
  const sentido = rotulo.lado === "direita" ? 1 : -1;
  const cotovelo = CENTRO.x + sentido * (RAIO_EXTERNO + 8);
  const fim = rotulo.x - sentido * 6;
  return `M${ancora.x},${ancora.y} L${cotovelo},${rotulo.y} L${fim},${rotulo.y}`;
}
