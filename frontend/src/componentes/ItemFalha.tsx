import type { Achado } from "../tipos.ts";
import Selo from "./Selo.tsx";
import SeloDePrioridade from "./SeloDePrioridade.tsx";
import { formatarNota, formatarPercentil } from "./formato.ts";
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
      <dl className="item-falha__dados">
        <div>
          <dt>CVSS</dt>
          <dd>{aviso.cvss === null ? "sem CVSS" : formatarNota(aviso.cvss)}</dd>
        </div>
        <div>
          <dt>Percentil EPSS</dt>
          <dd>{aviso.percentil_epss === null ? "sem EPSS" : formatarPercentil(aviso.percentil_epss)}</dd>
        </div>
        <div>
          <dt>Versões afetadas</dt>
          <dd>
            <code>{aviso.versoes_afetadas}</code>
          </dd>
        </div>
        <div>
          <dt>Corrigida em</dt>
          <dd>{aviso.versao_corrigida === null ? "sem versão corrigida" : <code>{aviso.versao_corrigida}</code>}</dd>
        </div>
      </dl>
    </li>
  );
}
