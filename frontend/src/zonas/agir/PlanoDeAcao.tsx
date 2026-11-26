import type { Acao } from "../../relatorio/tiposDoRelatorio.ts";
import ItemDoPlanoDeAcao from "./ItemDoPlanoDeAcao.tsx";
import "./PlanoDeAcao.css";

interface Props {
  acoes: Acao[];
  aoAbrirTarefa: (acao: Acao) => void;
}

export default function PlanoDeAcao({ acoes, aoAbrirTarefa }: Props) {
  const cabecalho = (
    <div>
      <h2 id="plano-de-acao-titulo">O que fazer agora</h2>
      <p>Correções em ordem de prioridade e, dentro dela, da maior nota para a menor.</p>
    </div>
  );
  if (acoes.length === 0) {
    return (
      <section className="plano-de-acao" aria-labelledby="plano-de-acao-titulo">
        {cabecalho}
        <p className="plano-de-acao__vazio">Nada a corrigir nesta gravação.</p>
      </section>
    );
  }
  return (
    <section className="plano-de-acao" aria-labelledby="plano-de-acao-titulo">
      {cabecalho}
      <ol className="plano-de-acao__lista">
        {acoes.map((acao, indice) => (
          <ItemDoPlanoDeAcao key={acao.id} acao={acao} posicao={indice + 1} aoAbrirTarefa={aoAbrirTarefa} />
        ))}
      </ol>
    </section>
  );
}
