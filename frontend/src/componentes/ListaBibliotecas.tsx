import type { Achado, Biblioteca } from "../tipos.ts";
import LinhaBiblioteca from "./LinhaBiblioteca.tsx";
import "./ListaBibliotecas.css";

interface Props {
  bibliotecas: Biblioteca[];
  achados: Achado[];
}

export default function ListaBibliotecas({ bibliotecas, achados }: Props) {
  return (
    <section className="lista-bibliotecas" aria-labelledby="lista-bibliotecas-titulo">
      <div>
        <h2 id="lista-bibliotecas-titulo">Bibliotecas encontradas</h2>
        <p>Abra uma biblioteca para ver onde ela apareceu no HAR e as falhas conhecidas.</p>
      </div>
      {bibliotecas.length === 0 ? (
        <p className="lista-bibliotecas__vazio">Nenhuma biblioteca confirmada nesta gravação.</p>
      ) : (
        <ul className="lista-bibliotecas__lista">
          {bibliotecas.map((biblioteca) => (
            <LinhaBiblioteca
              key={biblioteca.id}
              biblioteca={biblioteca}
              achados={achadosDaBiblioteca(biblioteca, achados)}
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
