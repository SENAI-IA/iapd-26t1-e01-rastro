import type { Camada } from "../relatorio/tiposDoRelatorio.ts";

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

const ANGULO_DO_TOPO = -90;
const VOLTA_COMPLETA = 360;
const ABERTURA_NO_TOPO = 44;
const FAIXAS_DE_ESPALHAMENTO = 3;
const DISTANCIA_ENTRE_FAIXAS = 6;
const DISTANCIA_DA_COLUNA_DE_ROTULOS = 222;
const LARGURA_DA_COLUNA_DE_ROTULOS = 175;
const ESPACO_ENTRE_ROTULOS = 27;
const FOLGA_DO_DISCO = 14;
const FOLGA_DO_COTOVELO = 8;
const FOLGA_ANTES_DO_ROTULO = 6;
const MARGEM = 18;

export interface Ponto {
  x: number;
  y: number;
}

export type Lado = "direita" | "esquerda";

export interface ItemComAncora<Item> {
  item: Item;
  ancora: Ponto;
}

interface ItemEmpilhado<Item> extends ItemComAncora<Item> {
  y: number;
}

export interface Rotulo<Item> extends ItemEmpilhado<Item> {
  lado: Lado;
  x: number;
}

function sentidoDoLado(lado: Lado): number {
  return lado === "direita" ? 1 : -1;
}

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
  return ANGULO_DO_TOPO + ABERTURA_NO_TOPO / 2 + fracao * (VOLTA_COMPLETA - ABERTURA_NO_TOPO);
}

export function pontoNoCirculo(raio: number, angulo: number): Ponto {
  const radianos = (angulo * Math.PI) / 180;
  return { x: CENTRO.x + raio * Math.cos(radianos), y: CENTRO.y + raio * Math.sin(radianos) };
}

export function raioComEspalhamento(camada: Camada, indice: number): number {
  const faixaEntreMenosUmEUm = (indice % FAIXAS_DE_ESPALHAMENTO) - 1;
  return RAIO_DA_CAMADA[camada] + faixaEntreMenosUmEUm * DISTANCIA_ENTRE_FAIXAS;
}

export function fatiaDoRastro(anguloFinal: number, abertura: number): string {
  const inicio = pontoNoCirculo(RAIO_EXTERNO, anguloFinal - abertura);
  const fim = pontoNoCirculo(RAIO_EXTERNO, anguloFinal);
  return `M${CENTRO.x},${CENTRO.y} L${inicio.x},${inicio.y} A${RAIO_EXTERNO},${RAIO_EXTERNO} 0 0 1 ${fim.x},${fim.y} Z`;
}

export function posicionarRotulos<Item>(itens: ItemComAncora<Item>[]): Rotulo<Item>[] {
  const lados: Lado[] = ["direita", "esquerda"];
  return lados.flatMap((lado) => {
    const doLado = itens
      .filter(({ ancora }) => ladoDoPonto(ancora) === lado)
      .sort((primeiro, segundo) => primeiro.ancora.y - segundo.ancora.y);
    const x = CENTRO.x + sentidoDoLado(lado) * DISTANCIA_DA_COLUNA_DE_ROTULOS;
    return empilharSemSobrepor(doLado).map((empilhado) => ({ ...empilhado, lado, x }));
  });
}

function empilharSemSobrepor<Item>(itens: ItemComAncora<Item>[]): ItemEmpilhado<Item>[] {
  const empilhados: ItemEmpilhado<Item>[] = [];
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
  const sentido = sentidoDoLado(rotulo.lado);
  const cotovelo = CENTRO.x + sentido * (RAIO_EXTERNO + FOLGA_DO_COTOVELO);
  const fim = rotulo.x - sentido * FOLGA_ANTES_DO_ROTULO;
  return `M${ancora.x},${ancora.y} L${cotovelo},${rotulo.y} L${fim},${rotulo.y}`;
}
