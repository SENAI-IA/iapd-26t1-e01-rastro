import type { NomeDaZona } from "../conteudo/zonas.ts";

export function idDaZona(zona: NomeDaZona): string {
  return `zona-${zona}`;
}

export function idDaLinhaDaBiblioteca(idDaBiblioteca: string): string {
  return `biblioteca-${idDaBiblioteca}`;
}

export function idDoPassoDoGuia(numero: number): string {
  return `passo-do-guia-${numero}`;
}
