const NUMERO = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const PERCENTIL = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 5 });
const INTEIRO = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const DATA = new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium", timeStyle: "short" });

export function formatarNota(nota: number): string {
  return NUMERO.format(nota);
}

export function formatarPercentil(percentil: number): string {
  return PERCENTIL.format(percentil);
}

export function formatarDuracao(segundos: number): string {
  return `${NUMERO.format(segundos)} s`;
}

export function formatarData(dataIso: string): string {
  const data = new Date(dataIso);
  return Number.isNaN(data.getTime()) ? dataIso : DATA.format(data);
}

export function plural(quantidade: number, singular: string, varios: string): string {
  return `${quantidade} ${quantidade === 1 ? singular : varios}`;
}

export function formatarTokens(tokens: number | null): string {
  return tokens === null ? "não informado" : INTEIRO.format(tokens);
}
