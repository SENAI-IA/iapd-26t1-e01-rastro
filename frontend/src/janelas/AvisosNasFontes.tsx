import type { OrigemDoDado } from "../telas/tiposDaTela.ts";
import DadosDoAviso from "./DadosDoAviso.tsx";

interface Props {
  origem: OrigemDoDado;
}

export default function AvisosNasFontes({ origem }: Props) {
  const { biblioteca, achados } = origem;
  if (biblioteca.motivo_nao_consultada !== null) {
    return <p className="painel-origem__texto">Não consultado: {biblioteca.motivo_nao_consultada}.</p>;
  }
  if (achados.length === 0) {
    return <p className="painel-origem__texto">Nenhum aviso atinge esta versão.</p>;
  }
  return (
    <ul className="painel-origem__lista">
      {achados.map(({ aviso }) => (
        <li key={aviso.ghsa}>
          <DadosDoAviso aviso={aviso} />
        </li>
      ))}
    </ul>
  );
}
