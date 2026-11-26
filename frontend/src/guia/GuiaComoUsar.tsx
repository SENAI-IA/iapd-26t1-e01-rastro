import { useState } from "react";
import { ANTES_DE_COMECAR, PASSOS_POR_MODO, PROBLEMAS, SEUS_DADOS, soDoModo, type ModoDeUso } from "../conteudo/guia.ts";
import CaixaDoGuia from "./CaixaDoGuia.tsx";
import EscolhaDoModo from "./EscolhaDoModo.tsx";
import ListaDoGuia from "./ListaDoGuia.tsx";
import PassoDoGuia from "./PassoDoGuia.tsx";
import ProblemaDoGuia from "./ProblemaDoGuia.tsx";
import ProgressoDoGuia from "./ProgressoDoGuia.tsx";
import { ID_DO_FIM_DO_GUIA } from "../calculosDeTela/identificadores.ts";
import { usarPassosFeitos } from "../hooks/usarPassosFeitos.ts";
import "./GuiaComoUsar.css";

interface Props {
  aoIrParaOPainel: (() => void) | null;
  medirAlturaDoCabecalhoFixo: () => number;
}

export default function GuiaComoUsar({ aoIrParaOPainel, medirAlturaDoCabecalhoFixo }: Props) {
  const [modo, setModo] = useState<ModoDeUso>("devtools");
  const passos = PASSOS_POR_MODO[modo];
  const { feitos, alternar, desmarcarTodos } = usarPassosFeitos(passos.length, medirAlturaDoCabecalhoFixo);

  const escolherModo = (novo: ModoDeUso) => {
    setModo(novo);
    desmarcarTodos();
  };

  return (
    <section className="guia-como-usar" aria-labelledby="guia-como-usar-titulo">
      <header className="guia-como-usar__topo">
        <h1 id="guia-como-usar-titulo">Como usar o Rastro</h1>
        <p>Do site ao relatório, em {passos.length} passos. Você só precisa do navegador e de um terminal.</p>
        <ProgressoDoGuia feitos={feitos.size} total={passos.length} />
      </header>
      <EscolhaDoModo modo={modo} aoEscolher={escolherModo} />
      <CaixaDoGuia titulo="Antes de começar">
        <ListaDoGuia itens={soDoModo(ANTES_DE_COMECAR, modo)} />
      </CaixaDoGuia>
      <ol className="guia-como-usar__passos">
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
        <button type="button" id={ID_DO_FIM_DO_GUIA} className="guia-como-usar__ir-para-o-painel" onClick={aoIrParaOPainel}>
          Ver o relatório desta análise
        </button>
      )}
      <div className="guia-como-usar__grade">
        <CaixaDoGuia titulo="Se algo der errado">
          {soDoModo(PROBLEMAS, modo).map((problema) => (
            <ProblemaDoGuia key={problema.sintoma} problema={problema} />
          ))}
        </CaixaDoGuia>
        <CaixaDoGuia titulo="Seus dados">
          <ListaDoGuia itens={soDoModo(SEUS_DADOS, modo)} />
        </CaixaDoGuia>
      </div>
    </section>
  );
}
