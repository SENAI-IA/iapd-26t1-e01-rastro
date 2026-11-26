import type { DadosDaIA } from "../../relatorio/tiposDoRelatorio.ts";
import ListaDeTravas from "./ListaDeTravas.tsx";
import UsoDaIA from "./UsoDaIA.tsx";
import Selo from "../../basicos/Selo.tsx";
import Termo from "../../basicos/Termo.tsx";
import "./PainelDaIA.css";

interface Props {
  ia: DadosDaIA;
  provedor: string | null;
}

export default function PainelDaIA({ ia, provedor }: Props) {
  return (
    <section className="painel-da-ia" aria-labelledby="painel-da-ia-titulo">
      <div className="painel-da-ia__cabecalho">
        <h2 id="painel-da-ia-titulo">
          <Selo tom="ia" icone="ia">
            IA
          </Selo>
          Onde a IA entrou nesta análise
        </h2>
        <p>A IA sugere, a regra confirma. A nota de risco e a prioridade vêm sempre da fórmula.</p>
      </div>
      <UsoDaIA ia={ia} provedor={provedor} />
      <div className="painel-da-ia__bloco">
        <h3>
          <Termo nome="Trava">Travas</Termo> acionadas
        </h3>
        <ListaDeTravas travas={ia.travas_acionadas} />
      </div>
    </section>
  );
}
