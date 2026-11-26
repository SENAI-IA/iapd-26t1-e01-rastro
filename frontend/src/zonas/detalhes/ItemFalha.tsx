import type { Achado } from "../../relatorio/tiposDoRelatorio.ts";
import DadosDaFalha from "./DadosDaFalha.tsx";
import Selo from "../../basicos/Selo.tsx";
import SeloDePrioridade from "../../basicos/SeloDePrioridade.tsx";
import { formatarNota } from "../../formatacao/formato.ts";
import "./ItemFalha.css";

interface Props {
  achado: Achado;
  aoVerOrigem: () => void;
}

export default function ItemFalha({ achado, aoVerOrigem }: Props) {
  const { aviso, nota } = achado;
  return (
    <li className="item-falha">
      <div className="item-falha__topo">
        <a href={aviso.link} target="_blank" rel="noopener noreferrer">
          {aviso.ghsa}
        </a>
        {aviso.cve !== null && <code>{aviso.cve}</code>}
        <span className="item-falha__selos">
          <SeloDePrioridade prioridade={nota.prioridade} />
          {nota.sem_epss && (
            <Selo tom="neutro" icone="info">
              Sem EPSS
            </Selo>
          )}
        </span>
        <button
          type="button"
          className="item-falha__nota"
          onClick={aoVerOrigem}
          title="Ver a origem e a conta da nota"
        >
          {nota.valor === null ? "Sem nota" : formatarNota(nota.valor)}
          <span className="item-falha__ver">ver a conta</span>
        </button>
      </div>
      <p className="item-falha__resumo">{aviso.resumo}</p>
      <DadosDaFalha aviso={aviso} />
    </li>
  );
}
