import type { Acao as DadosDaAcao } from "../tipos.ts";
import Acao from "./Acao.tsx";
import "./PlanoDeAcao.css";

interface Props {
  acoes: DadosDaAcao[];
}

export default function PlanoDeAcao({ acoes }: Props) {
  return (
    <section className="plano-de-acao" aria-labelledby="plano-de-acao-titulo">
      <div>
        <h2 id="plano-de-acao-titulo">O que fazer agora</h2>
        <p>Correções em ordem de prioridade e, dentro dela, da maior nota para a menor.</p>
      </div>
      {acoes.length === 0 ? (
        <p className="plano-de-acao__vazio">Nada a corrigir nesta gravação.</p>
      ) : (
        <ol className="plano-de-acao__lista">
          {acoes.map((acao, indice) => (
            <Acao key={acao.id} acao={acao} posicao={indice + 1} />
          ))}
        </ol>
      )}
    </section>
  );
}
