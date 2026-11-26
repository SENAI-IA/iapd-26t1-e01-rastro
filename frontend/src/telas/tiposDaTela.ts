import type { Achado, Biblioteca } from "../relatorio/tiposDoRelatorio.ts";

export type Tema = "claro" | "escuro";

export type Aba = "painel" | "pentest" | "como-usar";

export interface OrigemDoDado {
  biblioteca: Biblioteca;
  achados: Achado[];
}
