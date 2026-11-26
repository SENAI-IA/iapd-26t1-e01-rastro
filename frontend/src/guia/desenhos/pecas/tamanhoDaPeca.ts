export type TamanhoDaPeca = "grande" | "pequeno";

export const PREFIXO_DA_CLASSE: Record<TamanhoDaPeca, string> = {
  grande: "ilustracao",
  pequeno: "modo-anim",
};
