import type { TravaAcionada } from "../../relatorio/tiposDoRelatorio.ts";
import Selo from "../../basicos/Selo.tsx";

interface Props {
  travas: TravaAcionada[];
}

export default function ListaDeTravas({ travas }: Props) {
  if (travas.length === 0) {
    return <p className="painel-da-ia__vazio">Nenhuma trava precisou barrar nada nesta análise.</p>;
  }
  return (
    <ul className="painel-da-ia__lista">
      {travas.map((trava, indice) => (
        <li key={indice} className="painel-da-ia__trava">
          <Selo tom="serio" icone="triangulo">
            Trava "{trava.trava}"
          </Selo>
          <span>
            <b>Barrou:</b> {trava.alvo}
          </span>
          <span>
            <b>Por quê:</b> {trava.motivo}
          </span>
        </li>
      ))}
    </ul>
  );
}
