import type { Aviso } from "../relatorio/tiposDoRelatorio.ts";
import FonteDoCampo from "./FonteDoCampo.tsx";
import Termo from "../basicos/Termo.tsx";
import { formatarNota, formatarPercentil } from "../formatacao/formato.ts";

interface Props {
  aviso: Aviso;
}

export default function DadosDoAviso({ aviso }: Props) {
  return (
    <dl className="painel-origem-do-dado__dados">
      <dt>Aviso</dt>
      <dd>
        <a href={aviso.link} target="_blank" rel="noopener noreferrer">
          {aviso.ghsa}
        </a>
        {aviso.cve !== null && <code> · {aviso.cve}</code>}
        <FonteDoCampo aviso={aviso} campo="link" />
      </dd>
      <dt>Fontes</dt>
      <dd>{aviso.fontes.join(" · ")}</dd>
      <dt>Versões afetadas</dt>
      <dd>
        <code>{aviso.versoes_afetadas}</code>
        <FonteDoCampo aviso={aviso} campo="versoes_afetadas" />
      </dd>
      <dt>Corrigida em</dt>
      <dd>
        {aviso.versao_corrigida === null ? "sem versão corrigida" : <code>{aviso.versao_corrigida}</code>}
        <FonteDoCampo aviso={aviso} campo="versao_corrigida" />
      </dd>
      <dt>
        <Termo nome="CVSS" />
      </dt>
      <dd>
        {aviso.cvss === null ? "sem CVSS" : formatarNota(aviso.cvss)}
        <FonteDoCampo aviso={aviso} campo="cvss" />
      </dd>
      <dt>
        Percentil <Termo nome="EPSS" />
      </dt>
      <dd>
        {aviso.percentil_epss === null ? "sem EPSS" : formatarPercentil(aviso.percentil_epss)}
        <FonteDoCampo aviso={aviso} campo="percentil_epss" />
      </dd>
    </dl>
  );
}
