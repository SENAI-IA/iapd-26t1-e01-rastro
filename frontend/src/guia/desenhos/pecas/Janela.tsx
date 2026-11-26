import type { ReactNode } from "react";
import { PREFIXO_DA_CLASSE, type TamanhoDaPeca } from "./tamanhoDaPeca.ts";

interface MedidasDaJanela {
  temMoldura: boolean;
  inicioDaBarra: number;
  fimDaBarra: number;
  alturaDaBarra: number;
  botoes: number[];
  alturaDosBotoes: number;
  raioDosBotoes: number;
}

const MEDIDAS_DA_JANELA: Record<TamanhoDaPeca, MedidasDaJanela> = {
  grande: {
    temMoldura: true,
    inicioDaBarra: 8,
    fimDaBarra: 312,
    alturaDaBarra: 34,
    botoes: [22, 34, 46],
    alturaDosBotoes: 21,
    raioDosBotoes: 4,
  },
  pequeno: {
    temMoldura: false,
    inicioDaBarra: 0,
    fimDaBarra: 68,
    alturaDaBarra: 11,
    botoes: [7, 13],
    alturaDosBotoes: 6,
    raioDosBotoes: 1.6,
  },
};

interface Props {
  tamanho: TamanhoDaPeca;
  children: ReactNode;
}

export default function Janela({ tamanho, children }: Props) {
  const traco = `${PREFIXO_DA_CLASSE[tamanho]}__traco`;
  const medidas = MEDIDAS_DA_JANELA[tamanho];
  return (
    <>
      {medidas.temMoldura && <rect className={traco} x="8" y="8" width="304" height="174" rx="4" />}
      <line
        className={traco}
        x1={medidas.inicioDaBarra}
        y1={medidas.alturaDaBarra}
        x2={medidas.fimDaBarra}
        y2={medidas.alturaDaBarra}
      />
      {medidas.botoes.map((centroDoBotao) => (
        <circle key={centroDoBotao} className={traco} cx={centroDoBotao} cy={medidas.alturaDosBotoes} r={medidas.raioDosBotoes} />
      ))}
      {children}
    </>
  );
}
