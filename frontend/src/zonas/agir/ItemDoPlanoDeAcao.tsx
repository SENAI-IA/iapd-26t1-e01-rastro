import type { Acao } from "../../relatorio/tiposDoRelatorio.ts";
import Icone from "../../basicos/Icone.tsx";
import SeloDePrioridade from "../../basicos/SeloDePrioridade.tsx";
import { formatarNota } from "../../formatacao/formato.ts";
import "./ItemDoPlanoDeAcao.css";

interface Props {
  acao: Acao;
  posicao: number;
  aoAbrirTarefa: (acao: Acao) => void;
}

export default function ItemDoPlanoDeAcao({ acao, posicao, aoAbrirTarefa }: Props) {
  return (
    <li className={`item-do-plano-de-acao item-do-plano-de-acao--${acao.prioridade.replace(" ", "-")}`}>
      <span className="item-do-plano-de-acao__posicao">{posicao}</span>
      <div className="item-do-plano-de-acao__corpo">
        <h3 className="item-do-plano-de-acao__titulo">{acao.o_que_fazer}</h3>
        <p className="item-do-plano-de-acao__porque">{acao.porque}</p>
        <p className="item-do-plano-de-acao__impacto">{acao.impacto}</p>
        <div className="item-do-plano-de-acao__detalhes">
          <SeloDePrioridade prioridade={acao.prioridade} />
          {acao.nota !== null && <span>Nota {formatarNota(acao.nota)}</span>}
          <span>
            <Icone nome="pessoa" tamanho={12} />
            Quem resolve: {acao.quem_resolve}
          </span>
        </div>
        {acao.teste_verificacao !== null && (
          <div className="item-do-plano-de-acao__verificar">
            <p>
              <b>Como verificar:</b> {acao.teste_verificacao}
            </p>
            <span className="item-do-plano-de-acao__nota-ia">
              <Icone nome="triangulo" tamanho={12} />
              Sugerido pela IA: confira antes de usar.
            </span>
          </div>
        )}
        <button type="button" className="item-do-plano-de-acao__abrir-tarefa" onClick={() => aoAbrirTarefa(acao)}>
          <Icone nome="arquivo" tamanho={14} />
          Abrir task
        </button>
      </div>
    </li>
  );
}
