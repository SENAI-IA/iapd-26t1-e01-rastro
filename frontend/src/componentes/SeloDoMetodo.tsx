import type { MetodoDeIdentificacao } from "../tipos.ts";
import Selo from "./Selo.tsx";

interface Props {
  metodo: MetodoDeIdentificacao;
}

export default function SeloDoMetodo({ metodo }: Props) {
  if (metodo === "ia") {
    return (
      <Selo tom="ia" icone="ia">
        Encontrada pela IA
      </Selo>
    );
  }
  return (
    <Selo tom="neutro" icone="lupa">
      Por assinatura
    </Selo>
  );
}
