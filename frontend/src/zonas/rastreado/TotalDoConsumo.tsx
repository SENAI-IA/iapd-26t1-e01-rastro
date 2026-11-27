import type { DadosDaIA } from "../../relatorio/tiposDoRelatorio.ts";
import Termo from "../../basicos/Termo.tsx";
import { formatarCreditos, formatarTokens } from "../../formatacao/formato.ts";

interface Props {
  ia: DadosDaIA;
}

export default function TotalDoConsumo({ ia }: Props) {
  if (ia.tokens_total !== null) {
    return (
      <>
        , total de <Termo nome="Token">tokens</Termo>: {formatarTokens(ia.tokens_total)}
      </>
    );
  }
  if (ia.creditos_total != null) {
    return (
      <>
        , total de <Termo nome="Crédito">créditos</Termo>: {formatarCreditos(ia.creditos_total)}
      </>
    );
  }
  return <>, consumo: não informado</>;
}
