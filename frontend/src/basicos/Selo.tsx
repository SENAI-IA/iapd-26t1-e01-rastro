import type { ReactNode } from "react";
import Icone, { type NomeDoIcone } from "./Icone.tsx";
import "./Selo.css";

export type TomDoSelo = "critico" | "serio" | "neutro" | "bom" | "ia";

interface Props {
  tom: TomDoSelo;
  icone: NomeDoIcone;
  children: ReactNode;
}

export default function Selo({ tom, icone, children }: Props) {
  return (
    <span className={`selo selo--${tom}`}>
      <Icone nome={icone} tamanho={12} />
      {children}
    </span>
  );
}
