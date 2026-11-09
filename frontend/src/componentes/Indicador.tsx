import type { ReactNode } from "react";
import Icone, { type NomeDoIcone } from "./Icone.tsx";
import "./Indicador.css";

interface Props {
  titulo: string;
  icone: NomeDoIcone;
  valor: string;
  complemento?: string;
  selo?: ReactNode;
  descricao: ReactNode;
}

export default function Indicador({ titulo, icone, valor, complemento, selo, descricao }: Props) {
  return (
    <div className="indicador">
      <span className="indicador__titulo">
        <Icone nome={icone} />
        {titulo}
      </span>
      <div className="indicador__linha">
        <span className="indicador__valor">
          {valor}
          {complemento && <small> {complemento}</small>}
        </span>
        {selo}
      </div>
      <p className="indicador__descricao">{descricao}</p>
    </div>
  );
}
