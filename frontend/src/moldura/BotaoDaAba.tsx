import type { ReactNode } from "react";
import Icone, { type NomeDoIcone } from "../basicos/Icone.tsx";
import type { Aba } from "../telas/tiposDaTela.ts";

interface Props {
  aba: Aba;
  abaAtual: Aba;
  icone: NomeDoIcone;
  classeExtra?: string;
  aoTrocarAba: (aba: Aba) => void;
  children: ReactNode;
}

export default function BotaoDaAba({ aba, abaAtual, icone, classeExtra, aoTrocarAba, children }: Props) {
  return (
    <button
      type="button"
      className={classeExtra ? `barra-superior__aba ${classeExtra}` : "barra-superior__aba"}
      aria-current={aba === abaAtual ? "page" : undefined}
      onClick={() => aoTrocarAba(aba)}
    >
      <Icone nome={icone} />
      {children}
    </button>
  );
}
