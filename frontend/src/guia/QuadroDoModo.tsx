import type { ReactNode } from "react";

interface Props {
  posicao: number;
  numero: number;
  legenda: string;
  children: ReactNode;
}

export default function QuadroDoModo({ posicao, numero, legenda, children }: Props) {
  return (
    <g transform={`translate(${posicao} 2)`}>
      <rect
        className={`animacao-do-modo__traco animacao-do-modo__quadro animacao-do-modo__quadro--${numero}`}
        x="0"
        y="0"
        width="68"
        height="56"
        rx="3"
      />
      {children}
      <text className="animacao-do-modo__legenda" x="34" y="70" textAnchor="middle">
        {legenda}
      </text>
    </g>
  );
}
