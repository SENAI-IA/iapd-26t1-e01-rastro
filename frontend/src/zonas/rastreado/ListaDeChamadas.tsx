import type { ChamadaIA } from "../../relatorio/tiposDoRelatorio.ts";
import ChamadaDaIA from "./ChamadaDaIA.tsx";

interface Props {
  chamadas: ChamadaIA[];
}

export default function ListaDeChamadas({ chamadas }: Props) {
  if (chamadas.length === 0) {
    return <p className="painel-ia__vazio">Nenhuma chamada à IA: não havia achado para explicar.</p>;
  }
  return (
    <ol className="painel-ia__lista">
      {chamadas.map((chamada, indice) => (
        <ChamadaDaIA key={indice} chamada={chamada} />
      ))}
    </ol>
  );
}
