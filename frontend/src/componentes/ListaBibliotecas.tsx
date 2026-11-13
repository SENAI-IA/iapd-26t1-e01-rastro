import type { Achado, Biblioteca } from "../tipos.ts";
import LinhaBiblioteca from "./LinhaBiblioteca.tsx";
import type { OrigemDoDado } from "./PainelOrigemDoDado.tsx";
import Termo from "./Termo.tsx";
import "./ListaBibliotecas.css";

interface Props {
  bibliotecas: Biblioteca[];
  achados: Achado[];
  semJavascript: boolean;
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function ListaBibliotecas({ bibliotecas, achados, semJavascript, aoVerOrigem }: Props) {
  return (
    <section className="lista-bibliotecas" aria-labelledby="lista-bibliotecas-titulo">
      <div>
        <h2 id="lista-bibliotecas-titulo">Bibliotecas encontradas</h2>
        <p>Abra uma biblioteca para ver onde ela apareceu no <Termo nome="HAR" /> e as falhas conhecidas. Clique na nota para ver a conta.</p>
      </div>
      {bibliotecas.length === 0 && semJavascript ? (
        <p className="lista-bibliotecas__vazio">
          <strong>Nenhuma biblioteca pôde ser analisada:</strong> o <Termo nome="HAR" /> não trouxe nenhum script.
          Grave de novo com o filtro da aba Rede em <strong>Todos</strong> e o cache desativado.
        </p>
      ) : bibliotecas.length === 0 ? (
        <p className="lista-bibliotecas__vazio">Nenhuma biblioteca confirmada nesta gravação.</p>
      ) : (
        <ul className="lista-bibliotecas__lista">
          {bibliotecas.map((biblioteca) => (
            <LinhaBiblioteca
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

function achadosDaBiblioteca(biblioteca: Biblioteca, achados: Achado[]): Achado[] {
  return achados.filter((achado) => achado.biblioteca === biblioteca.id);
}
