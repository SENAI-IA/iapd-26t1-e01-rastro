import type { Achado, Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";
import ItemDaBiblioteca from "./ItemDaBiblioteca.tsx";
import ListaDeBibliotecasVazia from "./ListaDeBibliotecasVazia.tsx";
import type { OrigemDoDado } from "../../telas/tiposDaTela.ts";
import Termo from "../../basicos/Termo.tsx";
import "./ListaDeBibliotecas.css";

interface Props {
  bibliotecas: Biblioteca[];
  achados: Achado[];
  semJavascript: boolean;
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

function achadosDaBiblioteca(biblioteca: Biblioteca, achados: Achado[]): Achado[] {
  return achados.filter((achado) => achado.biblioteca === biblioteca.id);
}

export default function ListaDeBibliotecas({ bibliotecas, achados, semJavascript, aoVerOrigem }: Props) {
  return (
    <section className="lista-de-bibliotecas" aria-labelledby="lista-de-bibliotecas-titulo">
      <div>
        <h2 id="lista-de-bibliotecas-titulo">Bibliotecas encontradas</h2>
        <p>Abra uma biblioteca para ver onde ela apareceu no <Termo nome="HAR" /> e as falhas conhecidas. Clique na nota para ver a conta.</p>
      </div>
      {bibliotecas.length === 0 ? (
        <ListaDeBibliotecasVazia semJavascript={semJavascript} />
      ) : (
        <ul className="lista-de-bibliotecas__lista">
          {bibliotecas.map((biblioteca) => (
            <ItemDaBiblioteca
              key={biblioteca.id}
              biblioteca={biblioteca}
              achados={achadosDaBiblioteca(biblioteca, achados)}
              aoVerOrigem={aoVerOrigem}
            />
          ))}
        </ul>
      )}
    </section>
  );
}
