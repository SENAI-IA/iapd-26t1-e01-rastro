import { plural } from "../formatacao/formato.ts";

interface Props {
  feitos: number;
  total: number;
}

export default function ProgressoDoGuia({ feitos, total }: Props) {
  return (
    <div className="guia__progresso">
      <div className="guia__barra">
        <span style={{ width: `${(feitos / total) * 100}%` }} />
      </div>
      <span role="status">
        {feitos} de {plural(total, "passo feito", "passos feitos")}
      </span>
    </div>
  );
}
