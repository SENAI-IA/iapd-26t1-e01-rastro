import type { Biblioteca, TravaAcionada } from "../tipos.ts";
import Icone from "./Icone.tsx";
import ItemAConfirmar from "./ItemAConfirmar.tsx";
import "./ListaAConfirmar.css";

interface Props {
  bibliotecas: Biblioteca[];
  travasAcionadas: TravaAcionada[];
}

export default function ListaAConfirmar({ bibliotecas, travasAcionadas }: Props) {
  return (
    <section className="lista-a-confirmar" aria-labelledby="lista-a-confirmar-titulo">
      <div>
        <h2 id="lista-a-confirmar-titulo">A confirmar</h2>
        <p>
          <Icone nome="interrogacao" />
          Uma trava barrou estas bibliotecas. Elas ficam fora da nota, do resumo e do plano de ação até
          alguém conferir à mão.
        </p>
      </div>
      <ul className="lista-a-confirmar__lista">
        {bibliotecas.map((biblioteca) => (
          <ItemAConfirmar
            key={biblioteca.id}
            biblioteca={biblioteca}
            motivos={motivosDaBiblioteca(biblioteca, travasAcionadas)}
          />
        ))}
      </ul>
    </section>
  );
}

function motivosDaBiblioteca(biblioteca: Biblioteca, travasAcionadas: TravaAcionada[]): string[] {
  return travasAcionadas.filter((trava) => trava.alvo === biblioteca.id).map((trava) => trava.motivo);
}
