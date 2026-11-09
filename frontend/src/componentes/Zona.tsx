import type { ReactNode } from "react";
import { idDaZona, type Zona as DadosDaZona } from "../dados/zonas.ts";
import Icone from "./Icone.tsx";
import "./Zona.css";

interface Props {
  zona: DadosDaZona;
  aoFocar?: () => void;
  children: ReactNode;
}

export default function Zona({ zona, aoFocar, children }: Props) {
  return (
    <div id={idDaZona(zona.id)} className="zona">
      {aoFocar && (
        <div className="zona__cabecalho">
          <span className="zona__nome">{zona.nome}</span>
          <button
            type="button"
            className="zona__focar"
            onClick={aoFocar}
            aria-label={`Focar na zona ${zona.nome}`}
            title={`Ler só a zona ${zona.nome}, usando a tela toda`}
          >
            <Icone nome="alvo" />
            Focar
          </button>
        </div>
      )}
      {children}
    </div>
  );
}
