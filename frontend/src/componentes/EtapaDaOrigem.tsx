import type { ReactNode } from "react";
import "./EtapaDaOrigem.css";

interface Props {
  numero: number;
  titulo: string;
  children: ReactNode;
}

export default function EtapaDaOrigem({ numero, titulo, children }: Props) {
  return (
    <section className="etapa-da-origem">
      <h3>
        <span className="etapa-da-origem__numero">{numero}</span>
        {titulo}
      </h3>
      {children}
    </section>
  );
}
