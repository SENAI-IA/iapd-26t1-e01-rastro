import type { Biblioteca } from "../relatorio/tiposDoRelatorio.ts";
import EtapaDaOrigem from "./EtapaDaOrigem.tsx";

interface Props {
  biblioteca: Biblioteca;
}

export default function EtapaNoHar({ biblioteca }: Props) {
  return (
    <EtapaDaOrigem numero={1} titulo="No arquivo HAR">
      <ul className="painel-origem__lista">
        {biblioteca.evidencias.map((evidencia) => (
          <li key={evidencia.indice_requisicao}>
            <dl className="painel-origem__dados">
              <dt>Requisição</dt>
              <dd>
                <code>log.entries[{evidencia.indice_requisicao}]</code>
              </dd>
              <dt>URL</dt>
              <dd>
                <code>{evidencia.url}</code>
              </dd>
            </dl>
          </li>
        ))}
      </ul>
    </EtapaDaOrigem>
  );
}
