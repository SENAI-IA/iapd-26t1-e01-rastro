import type { ChamadaDaIA } from "../../relatorio/tiposDoRelatorio.ts";
import Icone from "../../basicos/Icone.tsx";
import Selo from "../../basicos/Selo.tsx";
import { formatarDuracao, formatarTokens } from "../../formatacao/formato.ts";
import "./ItemDaChamadaDaIA.css";

interface Props {
  chamada: ChamadaDaIA;
}

const NOMES_DAS_ETAPAS: Record<string, string> = {
  explicar_achado: "Explicar achado",
  identificar_bibliotecas: "Identificar bibliotecas",
};

export default function ItemDaChamadaDaIA({ chamada }: Props) {
  return (
    <li className="item-da-chamada-da-ia">
      <details>
        <summary className="item-da-chamada-da-ia__resumo">
          <span className="item-da-chamada-da-ia__seta">
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
          <span className="item-da-chamada-da-ia__medidas">
            <span>
              <Icone nome="relogio" tamanho={12} />
              {formatarDuracao(chamada.duracao_s)}
            </span>
            <span>Tokens: {formatarTokens(chamada.tokens)}</span>
          </span>
        </summary>
        <div className="item-da-chamada-da-ia__corpo">
          <h4>Entrada enviada</h4>
          <pre>{chamada.entrada}</pre>
          <h4>{chamada.sucesso ? "Resposta" : "Motivo da falha"}</h4>
          <pre>{chamada.resposta}</pre>
        </div>
      </details>
    </li>
  );
}
