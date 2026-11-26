import { comPlural } from "../formatacao/formato.ts";

interface Props {
  feitos: number;
  total: number;
}

export default function ProgressoDoGuia({ feitos, total }: Props) {
  return (
    <div className="guia-como-usar__progresso">
      <div className="guia-como-usar__barra">
        <span style={{ width: `${(feitos / total) * 100}%` }} />
      </div>
      <span role="status">
        {feitos} de {comPlural(total, "passo feito", "passos feitos")}
      </span>
    </div>
  );
}
