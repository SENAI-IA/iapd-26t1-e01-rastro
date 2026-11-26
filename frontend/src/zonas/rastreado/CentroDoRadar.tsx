import { CENTRO } from "../../calculosDeTela/geometriaDoRadar.ts";
import { formatarDuracao } from "../../formatacao/formato.ts";

interface Props {
  momento: number;
}

export default function CentroDoRadar({ momento }: Props) {
  return (
    <>
      <circle className="radar__centro" cx={CENTRO.x} cy={CENTRO.y} r={34} />
      <text className="radar__tempo" x={CENTRO.x} y={CENTRO.y + 3}>
        {formatarDuracao(momento / 1000)}
      </text>
      <text className="radar__legenda-tempo" x={CENTRO.x} y={CENTRO.y + 17}>
        de visita
      </text>
    </>
  );
}
