import { useState } from "react";
import type { Comando, PassoDoGuia as DadosDoPasso } from "../dados/guia.ts";
import Icone from "./Icone.tsx";
import IlustracaoDoGuia from "./IlustracaoDoGuia.tsx";
import TextoComMarcas from "./TextoComMarcas.tsx";
import "./PassoDoGuia.css";

interface Props {
  numero: number;
  passo: DadosDoPasso;
  feito: boolean;
  aoMarcar: () => void;
}

export function idDoPassoDoGuia(numero: number): string {
  return `passo-do-guia-${numero}`;
}

export default function PassoDoGuia({ numero, passo, feito, aoMarcar }: Props) {
  const [copiado, setCopiado] = useState<string | null>(null);

  const copiar = (comando: Comando) => {
    navigator.clipboard?.writeText(comando.texto).then(
      () => setCopiado(comando.sistema),
      () => setCopiado(null),
    );
  };

  return (
    <li
      id={idDoPassoDoGuia(numero)}
      tabIndex={-1}
      className={feito ? "passo-do-guia passo-do-guia--feito" : "passo-do-guia"}
    >
      <div className="passo-do-guia__numero" aria-hidden="true">
        {feito ? <Icone nome="certo" tamanho={18} /> : numero}
      </div>
      <div className="passo-do-guia__texto">
        <h2>
          <span className="passo-do-guia__leitor">Passo {numero}: </span>
          {passo.titulo}
        </h2>
        <p>
          <TextoComMarcas texto={passo.texto} />
        </p>
        {passo.comandos?.map((comando) => (
          <div key={comando.sistema} className="passo-do-guia__comando">
            <span className="passo-do-guia__sistema">{comando.sistema}</span>
            <code>{comando.texto}</code>
            <button
              type="button"
              className="passo-do-guia__copiar"
              onClick={() => copiar(comando)}
              aria-label={`Copiar o comando para ${comando.sistema}`}
            >
              {copiado === comando.sistema ? "Copiado" : "Copiar"}
            </button>
          </div>
        ))}
        {passo.dica && (
          <p className="passo-do-guia__dica">
            <TextoComMarcas texto={passo.dica} />
          </p>
        )}
        <button type="button" className="passo-do-guia__marcar" aria-pressed={feito} onClick={aoMarcar}>
          {feito ? "Feito" : "Marcar como feito"}
        </button>
      </div>
      <IlustracaoDoGuia ilustracao={passo.ilustracao} />
    </li>
  );
}
