import type { ChamadaIA } from "../tipos.ts";
import Icone from "./Icone.tsx";
import Selo from "./Selo.tsx";
import { formatarDuracao, formatarTokens } from "./formato.ts";
import "./ChamadaDaIA.css";

interface Props {
  chamada: ChamadaIA;
}

const NOMES_DAS_ETAPAS: Record<string, string> = {
  explicar_achado: "Explicar achado",
  identificar_bibliotecas: "Identificar bibliotecas",
};

export default function ChamadaDaIA({ chamada }: Props) {
  return (
    <li className="chamada-da-ia">
      <details>
        <summary className="chamada-da-ia__resumo">
          <span className="chamada-da-ia__seta">
            <Icone nome="seta" />
          </span>
          <b>{NOMES_DAS_ETAPAS[chamada.etapa] ?? chamada.etapa}</b>
          {chamada.sucesso ? (
            <Selo tom="bom" icone="certo">
              Respondeu
            </Selo>
          ) : (
            <Selo tom="serio" icone="erro">
              Falhou
            </Selo>
          )}
          <span className="chamada-da-ia__medidas">
            <span>
              <Icone nome="relogio" tamanho={12} />
              {formatarDuracao(chamada.duracao_s)}
            </span>
            <span>Tokens: {formatarTokens(chamada.tokens)}</span>
          </span>
        </summary>
        <div className="chamada-da-ia__corpo">
          <h4>Entrada enviada</h4>
          <pre>{chamada.entrada}</pre>
          <h4>{chamada.sucesso ? "Resposta" : "Motivo da falha"}</h4>
          <pre>{chamada.resposta}</pre>
        </div>
      </details>
    </li>
  );
}
