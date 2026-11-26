import type { Aviso, CampoComOrigem } from "../relatorio/tiposDoRelatorio.ts";

interface Props {
  aviso: Aviso;
  campo: CampoComOrigem;
}

export default function FonteDoCampo({ aviso, campo }: Props) {
  const fonte = aviso.origem_dos_campos[campo];
  if (fonte === undefined) {
    return null;
  }
  return <span className="painel-origem__fonte"> · {fonte}</span>;
}
