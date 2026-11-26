import type { Achado } from "../../relatorio/tiposDoRelatorio.ts";
import ItemDaFalha from "./ItemDaFalha.tsx";
import "./ListaDeFalhas.css";

interface Props {
  achados: Achado[];
  aoVerOrigem: (achado: Achado) => void;
}

export default function ListaDeFalhas({ achados, aoVerOrigem }: Props) {
  if (achados.length === 0) {
    return (
      <div className="lista-de-falhas">
        <h4>Falhas conhecidas</h4>
        <p className="lista-de-falhas__vazio">Nenhum aviso do GitHub Advisory atinge esta versão.</p>
      </div>
    );
  }
  return (
    <div className="lista-de-falhas">
      <h4>Falhas conhecidas</h4>
      <ol className="lista-de-falhas__lista">
        {achados.map((achado) => (
          <ItemDaFalha key={achado.aviso.ghsa} achado={achado} aoVerOrigem={() => aoVerOrigem(achado)} />
        ))}
      </ol>
    </div>
  );
}
