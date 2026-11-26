import type { Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";
import ComoConfirmarATrava from "./ComoConfirmarATrava.tsx";
import Evidencias from "./Evidencias.tsx";
import Selo from "../../basicos/Selo.tsx";
import SeloDoMetodo from "../../basicos/SeloDoMetodo.tsx";
import "./ItemAConfirmar.css";

interface Props {
  biblioteca: Biblioteca;
  motivos: string[];
}

export default function ItemAConfirmar({ biblioteca, motivos }: Props) {
  return (
    <li className="item-a-confirmar">
      <div className="item-a-confirmar__topo">
        <span className="item-a-confirmar__nome">
          <b>{biblioteca.pacote}</b> <code>{biblioteca.versao}</code>
        </span>
        <SeloDoMetodo metodo={biblioteca.metodo} />
        {biblioteca.travas_que_falharam.map((trava) => (
          <Selo key={trava} tom="serio" icone="triangulo">
            Barrada pela trava "{trava}"
          </Selo>
        ))}
      </div>
      {motivos.length > 0 && (
        <ul className="item-a-confirmar__motivos">
          {motivos.map((motivo) => (
            <li key={motivo}>{motivo}</li>
          ))}
        </ul>
      )}
      <div className="item-a-confirmar__como">
        <h4>Como confirmar à mão</h4>
        <ul>
          {biblioteca.travas_que_falharam.map((trava) => (
            <li key={trava}>
              <ComoConfirmarATrava trava={trava} biblioteca={biblioteca} />
            </li>
          ))}
        </ul>
      </div>
      <Evidencias evidencias={biblioteca.evidencias} />
    </li>
  );
}
