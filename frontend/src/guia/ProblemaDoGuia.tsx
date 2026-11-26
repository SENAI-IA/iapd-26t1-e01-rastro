import type { Problema } from "../conteudo/guia.ts";
import TextoComMarcas from "../basicos/TextoComMarcas.tsx";

interface Props {
  problema: Problema;
}

export default function ProblemaDoGuia({ problema }: Props) {
  return (
    <details className="guia__problema">
      <summary>{problema.sintoma}</summary>
      <p>
        <TextoComMarcas texto={problema.solucao} />
      </p>
    </details>
  );
}
