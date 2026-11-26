import type { MetodoDeIdentificacao } from "../relatorio/tiposDoRelatorio.ts";
import type { NomeDoIcone } from "./Icone.tsx";
import Selo, { type TomDoSelo } from "./Selo.tsx";

interface AparenciaDoMetodo {
  rotulo: string;
  tom: TomDoSelo;
  icone: NomeDoIcone;
}

const APARENCIA_DO_METODO: Record<MetodoDeIdentificacao, AparenciaDoMetodo> = {
  ia: { rotulo: "Encontrada pela IA", tom: "ia", icone: "ia" },
  assinatura: { rotulo: "Por assinatura", tom: "neutro", icone: "lupa" },
};

interface Props {
  metodo: MetodoDeIdentificacao;
}

export default function SeloDoMetodo({ metodo }: Props) {
  const { rotulo, tom, icone } = APARENCIA_DO_METODO[metodo];
  return (
    <Selo tom={tom} icone={icone}>
      {rotulo}
    </Selo>
  );
}
