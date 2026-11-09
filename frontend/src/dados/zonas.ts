export type NomeDaZona = "rastreado" | "agir" | "detalhes";

export interface Zona {
  id: NomeDaZona;
  nome: string;
}

export const ZONAS: Zona[] = [
  { id: "rastreado", nome: "Rastreado" },
  { id: "agir", nome: "Agir" },
  { id: "detalhes", nome: "Detalhes" },
];

export function idDaZona(zona: NomeDaZona): string {
  return `zona-${zona}`;
}
