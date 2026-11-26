import type { CategoriaDoPentest, ValidacaoDoPentest } from "../relatorio/tiposDoRelatorio.ts";

export type Veredito = "corrigir" | "em_ordem" | "sem_resposta";

export interface ValidacaoAgrupada {
  categoria: CategoriaDoPentest;
  veredito: Veredito;
  validacoes: ValidacaoDoPentest[];
}

function vereditoDe(validacoes: ValidacaoDoPentest[]): Veredito {
  if (validacoes.some((validacao) => validacao.situacao === "falhou")) {
    return "corrigir";
  }
  if (validacoes.some((validacao) => validacao.situacao === "passou")) {
    return "em_ordem";
  }
  return "sem_resposta";
}

export function agrupar(validacoes: ValidacaoDoPentest[]): ValidacaoAgrupada[] {
  const porCategoria = new Map<CategoriaDoPentest, ValidacaoDoPentest[]>();
  for (const validacao of validacoes) {
    porCategoria.set(validacao.categoria, [...(porCategoria.get(validacao.categoria) ?? []), validacao]);
  }
  return [...porCategoria].map(([categoria, doGrupo]) => ({
    categoria,
    veredito: vereditoDe(doGrupo),
    validacoes: doGrupo,
  }));
}

export function doVeredito(agrupadas: ValidacaoAgrupada[], veredito: Veredito): ValidacaoAgrupada[] {
  return agrupadas.filter((item) => item.veredito === veredito);
}

function enderecos(validacoes: ValidacaoDoPentest[]): number {
  return new Set(validacoes.map((validacao) => validacao.requisicao.url)).size;
}

export function contarEnderecos(grupo: ValidacaoAgrupada): { total: number; comFalha: number } {
  const queFalharam = grupo.validacoes.filter((validacao) => validacao.situacao === "falhou");
  return { total: enderecos(grupo.validacoes), comFalha: enderecos(queFalharam) };
}
