import type { Checagem } from "../tipos.ts";
import ItemChecagem from "./ItemChecagem.tsx";
import { plural } from "./formato.ts";
import "./ListaChecagens.css";

interface Props {
  checagens: Checagem[];
  comFalha: number;
  naoVerificadas: number;
}

export default function ListaChecagens({ checagens, comFalha, naoVerificadas }: Props) {
  return (
    <section className="lista-checagens" aria-labelledby="lista-checagens-titulo">
      <div>
        <h2 id="lista-checagens-titulo">Cabeçalhos e cookies</h2>
        <p>
          {plural(checagens.length, "checagem", "checagens")}: {comFalha} com falha,{" "}
          {plural(naoVerificadas, "não verificada", "não verificadas")}. Abra uma checagem para ver o detalhe e a
          evidência.
        </p>
      </div>
      <ul className="lista-checagens__lista">
        {checagens.map((checagem) => (
          <ItemChecagem key={checagem.id} checagem={checagem} />
        ))}
      </ul>
    </section>
  );
}
