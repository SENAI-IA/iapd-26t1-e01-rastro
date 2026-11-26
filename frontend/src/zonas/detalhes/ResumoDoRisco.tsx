import type { Achado, Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";
import Selo from "../../basicos/Selo.tsx";
import SeloDePrioridade from "../../basicos/SeloDePrioridade.tsx";
import { formatarNota, plural } from "../../formatacao/formato.ts";

interface Props {
  biblioteca: Biblioteca;
  achados: Achado[];
}

export default function ResumoDoRisco({ biblioteca, achados }: Props) {
  if (biblioteca.motivo_nao_consultada !== null) {
    return (
      <Selo tom="serio" icone="triangulo">
        Não consultada
      </Selo>
    );
  }
  if (achados.length === 0 || biblioteca.prioridade === null) {
    return (
      <Selo tom="bom" icone="certo">
        Sem falhas conhecidas
      </Selo>
    );
  }
  return (
    <>
      <span>{plural(achados.length, "falha", "falhas")}</span>
      <span className="linha-biblioteca__nota">
        {biblioteca.nota === null ? "Sem nota" : `Nota ${formatarNota(biblioteca.nota)}`}
      </span>
      <SeloDePrioridade prioridade={biblioteca.prioridade} />
    </>
  );
}
