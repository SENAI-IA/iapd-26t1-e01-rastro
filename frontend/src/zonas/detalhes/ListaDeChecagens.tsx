import type { Checagem } from "../../relatorio/tiposDoRelatorio.ts";
import ItemDaChecagem from "./ItemDaChecagem.tsx";
import { comPlural } from "../../formatacao/formato.ts";
import "./ListaDeChecagens.css";

interface Props {
  checagens: Checagem[];
  comFalha: number;
  naoVerificadas: number;
}

export default function ListaDeChecagens({ checagens, comFalha, naoVerificadas }: Props) {
  return (
    <section className="lista-de-checagens" aria-labelledby="lista-de-checagens-titulo">
      <div>
        <h2 id="lista-de-checagens-titulo">Cabeçalhos e cookies</h2>
        <p>
          {comPlural(checagens.length, "checagem", "checagens")}: {comFalha} com falha,{" "}
          {comPlural(naoVerificadas, "não verificada", "não verificadas")}. Abra uma checagem para ver o detalhe e a
          evidência.
        </p>
      </div>
      <ul className="lista-de-checagens__lista">
        {checagens.map((checagem) => (
          <ItemDaChecagem key={checagem.id} checagem={checagem} />
        ))}
      </ul>
    </section>
  );
}
