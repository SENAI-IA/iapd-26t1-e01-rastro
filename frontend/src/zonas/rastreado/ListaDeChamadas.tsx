import type { ChamadaDaIA } from "../../relatorio/tiposDoRelatorio.ts";
import ItemDaChamadaDaIA from "./ItemDaChamadaDaIA.tsx";

interface Props {
  chamadas: ChamadaDaIA[];
}

export default function ListaDeChamadas({ chamadas }: Props) {
  if (chamadas.length === 0) {
    return <p className="painel-da-ia__vazio">Nenhuma chamada à IA: não havia achado para explicar.</p>;
  }
  return (
    <ol className="painel-da-ia__lista">
      {chamadas.map((chamada, indice) => (
        <ItemDaChamadaDaIA key={indice} chamada={chamada} />
      ))}
    </ol>
  );
}
