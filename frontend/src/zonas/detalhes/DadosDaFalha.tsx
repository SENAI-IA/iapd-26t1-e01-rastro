import type { Aviso } from "../../relatorio/tiposDoRelatorio.ts";
import { formatarNota, formatarPercentil } from "../../formatacao/formato.ts";
import Termo from "../../basicos/Termo.tsx";

interface Props {
  aviso: Aviso;
}

export default function DadosDaFalha({ aviso }: Props) {
  return (
    <dl className="item-da-falha__dados">
      <div>
        <dt>
          <Termo nome="CVSS" />
        </dt>
        <dd>{aviso.cvss === null ? "sem CVSS" : formatarNota(aviso.cvss)}</dd>
      </div>
      <div>
        <dt>
          Percentil <Termo nome="EPSS" />
        </dt>
        <dd>{aviso.percentil_epss === null ? "sem EPSS" : formatarPercentil(aviso.percentil_epss)}</dd>
      </div>
      <div>
        <dt>Versões afetadas</dt>
        <dd>
          <code>{aviso.versoes_afetadas}</code>
        </dd>
      </div>
      <div>
        <dt>Corrigida em</dt>
        <dd>{aviso.versao_corrigida === null ? "sem versão corrigida" : <code>{aviso.versao_corrigida}</code>}</dd>
      </div>
    </dl>
  );
}
