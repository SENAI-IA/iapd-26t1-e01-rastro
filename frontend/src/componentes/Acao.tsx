import type { Acao as DadosDaAcao } from "../tipos.ts";
import Icone from "./Icone.tsx";
import SeloDePrioridade from "./SeloDePrioridade.tsx";
import { formatarNota } from "./formato.ts";
import "./Acao.css";

interface Props {
  acao: DadosDaAcao;
  posicao: number;
  aoAbrirTask: (acao: DadosDaAcao) => void;
}

export default function Acao({ acao, posicao, aoAbrirTask }: Props) {
  return (
    <li className={`acao acao--${acao.prioridade.replace(" ", "-")}`}>
      <span className="acao__posicao">{posicao}</span>
      <div className="acao__corpo">
        <h3 className="acao__titulo">{acao.o_que_fazer}</h3>
        <p className="acao__porque">{acao.porque}</p>
        <p className="acao__impacto">{acao.impacto}</p>
        <div className="acao__meta">
          <SeloDePrioridade prioridade={acao.prioridade} />
          {acao.nota !== null && <span>Nota {formatarNota(acao.nota)}</span>}
          <span>
            <Icone nome="pessoa" tamanho={12} />
            Quem resolve: {acao.quem_resolve}
          </span>
        </div>
        {acao.teste_verificacao !== null && (
          <div className="acao__verificar">
            <p>
              <b>Como verificar:</b> {acao.teste_verificacao}
            </p>
            <span className="acao__nota-ia">
              <Icone nome="triangulo" tamanho={12} />
              Sugerido pela IA: confira antes de usar.
            </span>
          </div>
        )}
        <button type="button" className="acao__abrir-task" onClick={() => aoAbrirTask(acao)}>
          <Icone nome="arquivo" tamanho={14} />
          Abrir task
        </button>
      </div>
    </li>
  );
}
