import type { ReactNode } from "react";
import type { Biblioteca } from "../tipos.ts";
import Evidencias from "./Evidencias.tsx";
import Selo from "./Selo.tsx";
import SeloDoMetodo from "./SeloDoMetodo.tsx";
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
            <li key={trava}>{comoConfirmar(trava, biblioteca)}</li>
          ))}
        </ul>
      </div>
      <Evidencias evidencias={biblioteca.evidencias} />
    </li>
  );
}

function comoConfirmar(trava: string, biblioteca: Biblioteca): ReactNode {
  const { pacote, versao } = biblioteca;
  const arquivo = <code>{biblioteca.evidencias[0]?.url ?? "o script"}</code>;
  switch (trava) {
    case "pacote existe":
      return (
        <>
          Abra{" "}
          <a href={`https://www.npmjs.com/package/${pacote}?activeTab=versions`} target="_blank" rel="noopener noreferrer">
            {pacote} no npm
          </a>{" "}
          e procure a versão <code>{versao}</code>. Se ela não estiver lá, confira no site do projeto se a versão
          existe e de onde o site a tirou.
        </>
      );
    case "trecho real":
      return <>Abra {arquivo} no HAR e procure o trecho que a IA citou. Se ele não estiver lá, a evidência foi inventada.</>;
    case "ancoragem":
      return (
        <>
          Procure <code>{versao}</code> no arquivo {arquivo} do HAR, perto do nome <code>{pacote}</code>.
        </>
      );
    case "código confere":
      return (
        <>
          Baixe{" "}
          <code>
            {pacote}@{versao}
          </code>{" "}
          do npm e procure, no código publicado, o trecho encontrado em {arquivo}.
        </>
      );
    default:
      return (
        <>
          Procure <code>{versao}</code> no arquivo {arquivo} do HAR e confira o nome e a versão no npm.
        </>
      );
  }
}
