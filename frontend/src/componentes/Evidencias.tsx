import type { Evidencia } from "../tipos.ts";
import Termo from "./Termo.tsx";
import "./Evidencias.css";

interface Props {
  evidencias: Evidencia[];
}

export default function Evidencias({ evidencias }: Props) {
  return (
    <div className="evidencias">
      <h4>
        Onde apareceu no <Termo nome="HAR" />
      </h4>
      <ul>
        {evidencias.map((evidencia) => (
          <li key={evidencia.indice_requisicao}>
            <code className="evidencias__url">{evidencia.url}</code>
            {evidencia.trecho !== null && <code className="evidencias__trecho">{evidencia.trecho}</code>}
          </li>
        ))}
      </ul>
    </div>
  );
}
