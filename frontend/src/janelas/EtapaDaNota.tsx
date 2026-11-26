import type { OrigemDoDado } from "../telas/tiposDaTela.ts";
import ContasDaNota from "./ContasDaNota.tsx";
import EtapaDaOrigem from "./EtapaDaOrigem.tsx";
import { formatarNota } from "../formatacao/formato.ts";

interface Props {
  origem: OrigemDoDado;
}

export default function EtapaDaNota({ origem }: Props) {
  const { biblioteca, achados } = origem;
  return (
    <EtapaDaOrigem numero={4} titulo="Cálculo da nota">
      <ContasDaNota origem={origem} />
      {achados.length > 1 && (
        <p className="painel-origem-do-dado__texto">
          Nota da biblioteca:{" "}
          <b>{biblioteca.nota === null ? "sem nota" : formatarNota(biblioteca.nota)}</b>, a maior entre as
          falhas.
        </p>
      )}
    </EtapaDaOrigem>
  );
}
