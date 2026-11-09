import type { Explicacao } from "../tipos.ts";
import Icone from "./Icone.tsx";
import Selo from "./Selo.tsx";
import "./ExplicacaoIA.css";

interface Props {
  explicacao: Explicacao;
}

export default function ExplicacaoIA({ explicacao }: Props) {
  if (!explicacao.gerada_por_ia) {
    return (
      <div className="explicacao-ia explicacao-ia--sem-ia">
        <Selo tom="neutro" icone="info">
          Sem explicação da IA
        </Selo>
        <p>
          <b>Resumo do aviso:</b> {explicacao.o_que_e}
        </p>
        <p className="explicacao-ia__nota">
          A IA não respondeu ou a resposta foi barrada por uma trava. O motivo está em "Onde a IA entrou".
        </p>
      </div>
    );
  }
  return (
    <div className="explicacao-ia">
      <Selo tom="ia" icone="ia">
        Explicação da IA
      </Selo>
      <dl>
        <dt>O que é</dt>
        <dd>{explicacao.o_que_e}</dd>
        <dt>Impacto</dt>
        <dd>{explicacao.impacto}</dd>
        <dt>Como corrigir</dt>
        <dd>{explicacao.como_corrigir}</dd>
        {explicacao.teste_verificacao && (
          <>
            <dt>Como verificar</dt>
            <dd>
              {explicacao.teste_verificacao}
              <span className="explicacao-ia__nota">
                <Icone nome="triangulo" tamanho={12} />
                Sugerido pela IA: confira antes de usar.
              </span>
            </dd>
          </>
        )}
      </dl>
    </div>
  );
}
