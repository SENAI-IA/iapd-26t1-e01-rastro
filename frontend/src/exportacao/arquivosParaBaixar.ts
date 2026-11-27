import type { Relatorio } from "../relatorio/tiposDoRelatorio.ts";
import { lerPaginaOriginal } from "./paginaOriginal.ts";
import { montarPlanilhaDeFalhas } from "./planilhaDeFalhas.ts";

export interface ArquivoParaBaixar {
  nome: string;
  conteudo: string;
  tipo: string;
}

const FORA_DO_NOME_DE_ARQUIVO = /[^a-z0-9.-]+/gi;
const TEMPO_PARA_O_NAVEGADOR_LER_O_ARQUIVO_MS = 1000;

function comecoDoNome(relatorio: Relatorio): string {
  const { site, har } = relatorio.analise;
  const nomeDoSite = (site ?? har.replace(/\.har$/i, "")).replace(FORA_DO_NOME_DE_ARQUIVO, "-");
  const dia = relatorio.analise.data.slice(0, 10);
  return `rastro-${nomeDoSite}-${dia}`;
}

export function planilhaDeFalhas(relatorio: Relatorio): ArquivoParaBaixar {
  return { nome: `${comecoDoNome(relatorio)}-falhas.csv`, conteudo: montarPlanilhaDeFalhas(relatorio), tipo: "text/csv" };
}

export function relatorioCompleto(relatorio: Relatorio): ArquivoParaBaixar {
  return { nome: `${comecoDoNome(relatorio)}.html`, conteudo: lerPaginaOriginal(), tipo: "text/html" };
}

export function baixarArquivo(arquivo: ArquivoParaBaixar): void {
  const endereco = URL.createObjectURL(new Blob([arquivo.conteudo], { type: `${arquivo.tipo};charset=utf-8` }));
  const link = document.createElement("a");
  link.href = endereco;
  link.download = arquivo.nome;
  document.body.append(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(endereco), TEMPO_PARA_O_NAVEGADOR_LER_O_ARQUIVO_MS);
}
