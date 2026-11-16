import { useState } from "react";
import {
  ANTES_DE_COMECAR,
  MODOS_DE_USO,
  PASSOS_POR_MODO,
  PROBLEMAS,
  SEUS_DADOS,
  valeNoModo,
  type ModoDeUso,
} from "../dados/guia.ts";
import AnimacaoDoModo from "./AnimacaoDoModo.tsx";
import { plural } from "./formato.ts";
import PassoDoGuia, { idDoPassoDoGuia } from "./PassoDoGuia.tsx";
import TextoComMarcas from "./TextoComMarcas.tsx";
import "./GuiaComoUsar.css";

const ID_DO_FIM_DO_GUIA = "guia-ir-para-o-painel";

function preferePoucoMovimento(): boolean {
  return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
}

function proximoPassoPendente(depoisDe: number, feitos: Set<number>, total: number): number | null {
  for (let indice = depoisDe + 1; indice < total; indice++) {
    if (!feitos.has(indice)) {
      return indice;
    }
  }
  return null;
}

function rolarAte(elemento: HTMLElement) {
  const alturaDoTopo = document.querySelector<HTMLElement>(".app__topo")?.offsetHeight ?? 0;
  window.scrollTo({
    top: elemento.getBoundingClientRect().top + window.scrollY - alturaDoTopo - 12,
    behavior: preferePoucoMovimento() ? "auto" : "smooth",
  });
  elemento.focus({ preventScroll: true });
}

interface Props {
  aoIrParaOPainel: (() => void) | null;
}

export default function GuiaComoUsar({ aoIrParaOPainel }: Props) {
  const [modo, setModo] = useState<ModoDeUso>("devtools");
  const [feitos, setFeitos] = useState<Set<number>>(new Set());
  const passos = PASSOS_POR_MODO[modo];
  const total = passos.length;

  const escolherModo = (novo: ModoDeUso) => {
    setModo(novo);
    setFeitos(new Set());
  };

  const alternar = (indice: number) => {
    const novos = new Set(feitos);
    if (novos.has(indice)) {
      novos.delete(indice);
      setFeitos(novos);
      return;
    }
    novos.add(indice);
    setFeitos(novos);
    const proximo = proximoPassoPendente(indice, novos, total);
    const destino = document.getElementById(
      proximo === null ? ID_DO_FIM_DO_GUIA : idDoPassoDoGuia(proximo + 1),
    );
    if (destino) {
      requestAnimationFrame(() => rolarAte(destino));
    }
  };

  return (
    <section className="guia" aria-labelledby="guia-titulo">
      <header className="guia__topo">
        <h1 id="guia-titulo">Como usar o Rastro</h1>
        <p>Do site ao relatório, em {total} passos. Você só precisa do navegador e de um terminal.</p>
        <div className="guia__progresso">
          <div className="guia__barra">
            <span style={{ width: `${(feitos.size / total) * 100}%` }} />
          </div>
          <span role="status">
            {feitos.size} de {plural(total, "passo feito", "passos feitos")}
          </span>
        </div>
      </header>

      <fieldset className="guia__modos">
        <legend>Como você quer gravar a visita ao site?</legend>
        {MODOS_DE_USO.map((opcao) => (
          <label
            key={opcao.modo}
            className={opcao.modo === modo ? "guia__modo guia__modo--escolhido" : "guia__modo"}
          >
            <input
              type="radio"
              name="guia-modo"
              value={opcao.modo}
              checked={opcao.modo === modo}
              onChange={() => escolherModo(opcao.modo)}
            />
            <AnimacaoDoModo modo={opcao.modo} />
            <span className="guia__modo-titulo">{opcao.titulo}</span>
            <span className="guia__modo-resumo">{opcao.resumo}</span>
          </label>
        ))}
      </fieldset>

      <div className="guia__caixa">
        <h2>Antes de começar</h2>
        <ul>
          {ANTES_DE_COMECAR.filter((item) => valeNoModo(item, modo)).map((item) => (
            <li key={item.texto}>
              <TextoComMarcas texto={item.texto} />
            </li>
          ))}
        </ul>
      </div>

      <ol className="guia__passos">
        {passos.map((passo, indice) => (
          <PassoDoGuia
            key={`${modo}-${passo.titulo}`}
            numero={indice + 1}
            passo={passo}
            feito={feitos.has(indice)}
            aoMarcar={() => alternar(indice)}
          />
        ))}
      </ol>

      {aoIrParaOPainel && (
        <button
          type="button"
          id={ID_DO_FIM_DO_GUIA}
          className="guia__ir-para-o-painel"
          onClick={aoIrParaOPainel}
        >
          Ver o relatório desta análise
        </button>
      )}

      <div className="guia__grade">
        <div className="guia__caixa">
          <h2>Se algo der errado</h2>
          {PROBLEMAS.filter((problema) => valeNoModo(problema, modo)).map((problema) => (
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
            {SEUS_DADOS.filter((item) => valeNoModo(item, modo)).map((item) => (
              <li key={item.texto}>
                <TextoComMarcas texto={item.texto} />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
