import type { Achado } from "../tipos.ts";
import ItemFalha from "./ItemFalha.tsx";
import "./ListaFalhas.css";

interface Props {
  achados: Achado[];
}

export default function ListaFalhas({ achados }: Props) {
  return (
    <div className="lista-falhas">
      <h4>Falhas conhecidas</h4>
      {achados.length === 0 ? (
        <p className="lista-falhas__vazio">Nenhum aviso do GitHub Advisory atinge esta versão.</p>
      ) : (
        <ol className="lista-falhas__lista">
          {achados.map((achado) => (
            <ItemFalha key={achado.aviso.ghsa} achado={achado} />
          ))}
        </ol>
      )}
    </div>
  );
}
