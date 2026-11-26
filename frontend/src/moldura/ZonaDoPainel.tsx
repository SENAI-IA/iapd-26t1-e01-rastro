import type { ReactNode } from "react";
import type { DescricaoDaZona } from "../conteudo/zonas.ts";
import { idDaZona } from "../calculosDeTela/identificadores.ts";
import Icone from "../basicos/Icone.tsx";
import "./ZonaDoPainel.css";

interface Props {
  zona: DescricaoDaZona;
  aoFocar?: () => void;
  children: ReactNode;
}

export default function ZonaDoPainel({ zona, aoFocar, children }: Props) {
  return (
    <div id={idDaZona(zona.id)} className="zona-do-painel">
      {aoFocar && (
        <div className="zona-do-painel__cabecalho">
          <span className="zona-do-painel__nome">{zona.nome}</span>
          <button
            type="button"
            className="zona-do-painel__focar"
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
