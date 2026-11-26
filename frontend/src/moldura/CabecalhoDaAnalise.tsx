import type { DadosDaAnalise } from "../relatorio/tiposDoRelatorio.ts";
import Icone from "../basicos/Icone.tsx";
import { formatarData, formatarDuracao } from "../formatacao/formato.ts";
import "./CabecalhoDaAnalise.css";

interface Props {
  analise: DadosDaAnalise;
}

export default function CabecalhoDaAnalise({ analise }: Props) {
  return (
    <div className="cabecalho-da-analise">
      <span className="cabecalho-da-analise__icone">
        <Icone nome="globo" tamanho={22} />
      </span>
      <div className="cabecalho-da-analise__texto">
        <span className="cabecalho-da-analise__rotulo">{analise.site ? "Site analisado" : "Gravação analisada"}</span>
        <h1>{analise.site ?? analise.har}</h1>
        <p className="cabecalho-da-analise__detalhes">
          <span>
            <Icone nome="arquivo" /> Gravação <code>{analise.har}</code>
          </span>
          <span>
            <Icone nome="relogio" /> Analisado em {formatarData(analise.data)} ({formatarDuracao(analise.duracao_s)})
          </span>
          <span>
            <Icone nome="ia" /> {analise.ia ? `IA: ${analise.ia}` : "Sem IA"}
          </span>
        </p>
      </div>
    </div>
  );
}
