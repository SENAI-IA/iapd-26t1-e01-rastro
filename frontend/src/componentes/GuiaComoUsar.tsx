import { useState } from "react";
import { ANTES_DE_COMECAR, PASSOS_DO_GUIA, PROBLEMAS, SEUS_DADOS } from "../dados/guia.ts";
import { plural } from "./formato.ts";
import PassoDoGuia from "./PassoDoGuia.tsx";
import TextoComMarcas from "./TextoComMarcas.tsx";
import "./GuiaComoUsar.css";

interface Props {
  aoIrParaOPainel: (() => void) | null;
}

export default function GuiaComoUsar({ aoIrParaOPainel }: Props) {
  const [feitos, setFeitos] = useState<Set<number>>(new Set());
  const total = PASSOS_DO_GUIA.length;

  const alternar = (indice: number) => {
    const novos = new Set(feitos);
    if (novos.has(indice)) {
      novos.delete(indice);
    } else {
      novos.add(indice);
    }
    setFeitos(novos);
  };

  return (
    <section className="guia" aria-labelledby="guia-titulo">
      <header className="guia__topo">
        <h1 id="guia-titulo">Como usar o Rastro</h1>
        <p>Do site gravado no navegador ao relatório, em {total} passos. Você só precisa do navegador e de um terminal.</p>
        <div className="guia__progresso">
          <div className="guia__barra">
            <span style={{ width: `${(feitos.size / total) * 100}%` }} />
          </div>
          <span role="status">
            {feitos.size} de {plural(total, "passo feito", "passos feitos")}
          </span>
        </div>
      </header>

      <div className="guia__caixa">
        <h2>Antes de começar</h2>
        <ul>
          {ANTES_DE_COMECAR.map((item) => (
            <li key={item}>
              <TextoComMarcas texto={item} />
            </li>
          ))}
        </ul>
      </div>

      <ol className="guia__passos">
        {PASSOS_DO_GUIA.map((passo, indice) => (
          <PassoDoGuia
            key={passo.titulo}
            numero={indice + 1}
            passo={passo}
            feito={feitos.has(indice)}
            aoMarcar={() => alternar(indice)}
          />
        ))}
      </ol>

      {aoIrParaOPainel && (
        <button type="button" className="guia__ir-para-o-painel" onClick={aoIrParaOPainel}>
          Ver o relatório desta análise
        </button>
      )}

      <div className="guia__grade">
        <div className="guia__caixa">
          <h2>Se algo der errado</h2>
          {PROBLEMAS.map((problema) => (
            <details key={problema.sintoma} className="guia__problema">
              <summary>{problema.sintoma}</summary>
              <p>
                <TextoComMarcas texto={problema.solucao} />
              </p>
            </details>
          ))}
        </div>
        <div className="guia__caixa">
          <h2>Seus dados</h2>
          <ul>
            {SEUS_DADOS.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
