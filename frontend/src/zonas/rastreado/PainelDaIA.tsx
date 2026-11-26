import type { DadosDaIA } from "../../relatorio/tiposDoRelatorio.ts";
import ListaDeChamadas from "./ListaDeChamadas.tsx";
import AvisoDeIADesligada from "./AvisoDeIADesligada.tsx";
import ComparacaoComESemIA from "./ComparacaoComESemIA.tsx";
import ListaDeTravas from "./ListaDeTravas.tsx";
import Selo from "../../basicos/Selo.tsx";
import { formatarTokens, comPlural } from "../../formatacao/formato.ts";
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
      {provedor === null ? (
        <AvisoDeIADesligada />
      ) : (
        <>
          {ia.com_e_sem_ia && <ComparacaoComESemIA comparacao={ia.com_e_sem_ia} />}
          <div className="painel-da-ia__bloco">
            <h3>O que a IA recebeu e devolveu</h3>
            <p>
              Provedor <code>{provedor}</code>: {comPlural(ia.chamadas.length, "chamada", "chamadas")}, total de{" "}
              <Termo nome="Token">tokens</Termo>: {formatarTokens(ia.tokens_total)}. A IA recebe só trechos
              escolhidos pelo Rastro, sem cookies, senhas ou tokens de sessão.
            </p>
            <ListaDeChamadas chamadas={ia.chamadas} />
          </div>
        </>
      )}
      <div className="painel-da-ia__bloco">
        <h3>
          <Termo nome="Trava">Travas</Termo> acionadas
        </h3>
        <ListaDeTravas travas={ia.travas_acionadas} />
      </div>
    </section>
  );
}
