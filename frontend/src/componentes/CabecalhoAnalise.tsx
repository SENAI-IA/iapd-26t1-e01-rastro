import type { DadosDaAnalise } from "../tipos.ts";
import Icone from "./Icone.tsx";
import { formatarData, formatarDuracao } from "./formato.ts";
import "./CabecalhoAnalise.css";

interface Props {
  analise: DadosDaAnalise;
}

export default function CabecalhoAnalise({ analise }: Props) {
  return (
    <div className="cabecalho-analise">
      <span className="cabecalho-analise__icone">
        <Icone nome="globo" tamanho={22} />
      </span>
      <div className="cabecalho-analise__texto">
        <span className="cabecalho-analise__rotulo">{analise.site ? "Site analisado" : "Gravação analisada"}</span>
        <h1>{analise.site ?? analise.har}</h1>
        <p className="cabecalho-analise__meta">
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
