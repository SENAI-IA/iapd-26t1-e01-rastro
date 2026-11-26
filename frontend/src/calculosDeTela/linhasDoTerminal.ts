export type DestaqueDaLinha = "comando" | "continuacao" | "saida" | "resultado";

export interface LinhaDoTerminal {
  texto: string;
  destaque: DestaqueDaLinha;
}

export interface LinhaPosicionada extends LinhaDoTerminal {
  y: number;
  ordemDeAparecer: number;
}

const PRIMEIRA_LINHA = 60;
const ENTRE_LINHAS = 18;
const DEPOIS_DO_COMANDO = 24;
const ANTES_DO_RESULTADO = 26;
export const CURSOR_ABAIXO_DA_ULTIMA_LINHA = 10;

function espacoAntes(linha: LinhaDoTerminal, anterior: LinhaDoTerminal): number {
  if (linha.destaque === "resultado") {
    return ANTES_DO_RESULTADO;
  }
  const anteriorEraComando = anterior.destaque === "comando" || anterior.destaque === "continuacao";
  if (anteriorEraComando && linha.destaque === "saida") {
    return DEPOIS_DO_COMANDO;
  }
  return ENTRE_LINHAS;
}

function posicionarDepoisDe(linha: LinhaDoTerminal, anterior: LinhaPosicionada | undefined): LinhaPosicionada {
  if (anterior === undefined) {
    return { ...linha, y: PRIMEIRA_LINHA, ordemDeAparecer: 1 };
  }
  const mesmaVez = linha.destaque === "continuacao";
  return {
    ...linha,
    y: anterior.y + espacoAntes(linha, anterior),
    ordemDeAparecer: mesmaVez ? anterior.ordemDeAparecer : anterior.ordemDeAparecer + 1,
  };
}

export function posicionarLinhas(linhas: LinhaDoTerminal[]): LinhaPosicionada[] {
  const posicionadas: LinhaPosicionada[] = [];
  for (const linha of linhas) {
    posicionadas.push(posicionarDepoisDe(linha, posicionadas.at(-1)));
  }
  return posicionadas;
}
