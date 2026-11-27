const UMA_CASA_DECIMAL = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const PERCENTIL = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 5 });
const INTEIRO = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const DUAS_CASAS_DECIMAIS = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const DATA = new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium", timeStyle: "short" });

export function formatarNota(nota: number): string {
  return UMA_CASA_DECIMAL.format(nota);
}

export function formatarPercentil(percentil: number): string {
  return PERCENTIL.format(percentil);
}

export function formatarDuracao(segundos: number): string {
  return `${UMA_CASA_DECIMAL.format(segundos)} s`;
}

export function formatarData(dataIso: string): string {
  const data = new Date(dataIso);
  return Number.isNaN(data.getTime()) ? dataIso : DATA.format(data);
}

export function comPlural(quantidade: number, singular: string, varios: string): string {
  return `${quantidade} ${quantidade === 1 ? singular : varios}`;
}

export function formatarTokens(tokens: number | null): string {
  return tokens === null ? "não informado" : INTEIRO.format(tokens);
}

export function formatarCreditos(creditos: number): string {
  return DUAS_CASAS_DECIMAIS.format(creditos);
}

export function descreverConsumo(tokens: number | null, creditos: number | null | undefined): string {
  if (tokens !== null) {
    return `Tokens: ${formatarTokens(tokens)}`;
  }
  if (creditos != null) {
    return `Créditos: ${formatarCreditos(creditos)}`;
  }
  return "Consumo: não informado";
}

export function textoDoNpm(conferida: boolean | null): string {
  if (conferida === null) {
    return "não respondeu; versão não conferida";
  }
  return conferida ? "versão publicada" : "versão não encontrada";
}

export function escreverStatus(status: number | null): string {
  return status === null ? "sem resposta" : `status ${status}`;
}

export function caminhoDaUrl(url: string): string {
  try {
    return new URL(url).pathname;
  } catch {
    return url;
  }
}
