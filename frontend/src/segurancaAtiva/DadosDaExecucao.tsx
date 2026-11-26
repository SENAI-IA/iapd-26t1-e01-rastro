import type { ResultadoDoPentest } from "../relatorio/tiposDoRelatorio.ts";
import { formatarData } from "../formatacao/formato.ts";

interface Props {
  pentest: ResultadoDoPentest;
}

export default function DadosDaExecucao({ pentest }: Props) {
  return (
    <dl className="painel-da-seguranca-ativa__origem">
      <div>
        <dt>Site testado</dt>
        <dd>{pentest.site}</dd>
      </div>
      <div>
        <dt>HAR de origem</dt>
        <dd><code>{pentest.har}</code></dd>
      </div>
      <div>
        <dt>Executado em</dt>
        <dd>{formatarData(pentest.executado_em)}</dd>
      </div>
      <div>
        <dt>Endereços conferidos</dt>
        <dd>{pentest.requisicoes_enviadas} de até {pentest.limite_de_requisicoes}</dd>
      </div>
    </dl>
  );
}
