import type { DadosDaIA } from "../../relatorio/tiposDoRelatorio.ts";
import ListaDeChamadas from "./ListaDeChamadas.tsx";
import AvisoDeIADesligada from "./AvisoDeIADesligada.tsx";
import ComparacaoComESemIA from "./ComparacaoComESemIA.tsx";
import { formatarTokens, comPlural } from "../../formatacao/formato.ts";
import Termo from "../../basicos/Termo.tsx";

interface Props {
  ia: DadosDaIA;
  provedor: string | null;
}

export default function UsoDaIA({ ia, provedor }: Props) {
  if (provedor === null) {
    return <AvisoDeIADesligada />;
  }
  return (
    <>
      {ia.com_e_sem_ia && <ComparacaoComESemIA comparacao={ia.com_e_sem_ia} />}
      <div className="painel-da-ia__bloco">
        <h3>O que a IA recebeu e devolveu</h3>
        <p>
          Provedor <code>{provedor}</code>: {comPlural(ia.chamadas.length, "chamada", "chamadas")}, total de{" "}
          <Termo nome="Token">tokens</Termo>: {formatarTokens(ia.tokens_total)}. A IA recebe só trechos
          escolhidos pelo Rastro, sem cookies, senhas ou tokens de sessão.
        </p>
        <ListaDeChamadas chamadas={ia.chamadas} />
      </div>
    </>
  );
}
