export type NomeDaZona = "rastreado" | "agir" | "detalhes";

export interface DescricaoDaZona {
  id: NomeDaZona;
  nome: string;
}

export const ZONAS: DescricaoDaZona[] = [
  { id: "rastreado", nome: "Rastreado" },
  { id: "agir", nome: "Agir" },
  { id: "detalhes", nome: "Detalhes" },
];
