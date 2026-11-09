import type { Prioridade } from "../tipos.ts";
import type { NomeDoIcone } from "./Icone.tsx";
import Selo, { type TomDoSelo } from "./Selo.tsx";

interface Aparencia {
  rotulo: string;
  tom: TomDoSelo;
  icone: NomeDoIcone;
}

const APARENCIA: Record<Prioridade, Aparencia> = {
  alta: { rotulo: "alta", tom: "critico", icone: "octogono" },
  media: { rotulo: "média", tom: "serio", icone: "triangulo" },
  baixa: { rotulo: "baixa", tom: "neutro", icone: "info" },
  "a avaliar": { rotulo: "a avaliar", tom: "neutro", icone: "interrogacao" },
};

interface Props {
  prioridade: Prioridade;
}

export default function SeloDePrioridade({ prioridade }: Props) {
  const { rotulo, tom, icone } = APARENCIA[prioridade];
  return (
    <Selo tom={tom} icone={icone}>
      Prioridade {rotulo}
    </Selo>
  );
}
