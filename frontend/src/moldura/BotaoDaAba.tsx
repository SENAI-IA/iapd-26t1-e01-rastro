import type { ReactNode } from "react";
import Icone, { type NomeDoIcone } from "../basicos/Icone.tsx";
import type { Tela } from "../telas/tiposDaTela.ts";

interface Props {
  tela: Tela;
  telaAberta: Tela;
  icone: NomeDoIcone;
  classeExtra?: string;
  aoTrocarTela: (tela: Tela) => void;
  children: ReactNode;
}

export default function BotaoDaAba({ tela, telaAberta, icone, classeExtra, aoTrocarTela, children }: Props) {
  return (
    <button
      type="button"
      className={classeExtra ? `barra-superior__tela ${classeExtra}` : "barra-superior__tela"}
      aria-current={tela === telaAberta ? "page" : undefined}
      onClick={() => aoTrocarTela(tela)}
    >
      <Icone nome={icone} />
      {children}
    </button>
  );
}
