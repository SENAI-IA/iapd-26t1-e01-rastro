import { PREFIXO_DA_CLASSE, type TamanhoDaPeca } from "./tamanhoDaPeca.ts";

interface MedidasDoRobo {
  largura: number;
  altura: number;
  canto: number;
  topoDaAntena: number;
  pontaDaAntena: number;
  raioDaPonta: number;
  distanciaDosOlhos: number;
  raioDoOlho: number;
  classeDoOlho: string;
}

const MEDIDAS_DO_ROBO: Record<TamanhoDaPeca, MedidasDoRobo> = {
  grande: {
    largura: 20,
    altura: 16,
    canto: 3,
    topoDaAntena: -13,
    pontaDaAntena: -14.5,
    raioDaPonta: 2,
    distanciaDosOlhos: 4,
    raioDoOlho: 2,
    classeDoOlho: "ilustracao-do-guia__olho",
  },
  pequeno: {
    largura: 12,
    altura: 10,
    canto: 2,
    topoDaAntena: -8,
    pontaDaAntena: -9,
    raioDaPonta: 1.4,
    distanciaDosOlhos: 2.5,
    raioDoOlho: 1.2,
    classeDoOlho: "animacao-do-modo__ponto",
  },
};

interface Props {
  x: number;
  y: number;
  tamanho: TamanhoDaPeca;
}

export default function Robo({ x, y, tamanho }: Props) {
  const prefixo = PREFIXO_DA_CLASSE[tamanho];
  const medidas = MEDIDAS_DO_ROBO[tamanho];
  const traco = `${prefixo}__traco ${prefixo}__traco--destaque`;
  return (
    <g transform={`translate(${x} ${y})`}>
      <g className={`${prefixo}__robo`}>
        <line className={traco} x1="0" y1={-medidas.altura / 2} x2="0" y2={medidas.topoDaAntena} />
        <circle className={medidas.classeDoOlho} cx="0" cy={medidas.pontaDaAntena} r={medidas.raioDaPonta} />
        <rect
          className={`${traco} ${prefixo}__cabeca`}
          x={-medidas.largura / 2}
          y={-medidas.altura / 2}
          width={medidas.largura}
          height={medidas.altura}
          rx={medidas.canto}
        />
        <circle className={medidas.classeDoOlho} cx={-medidas.distanciaDosOlhos} cy="0" r={medidas.raioDoOlho} />
        <circle className={medidas.classeDoOlho} cx={medidas.distanciaDosOlhos} cy="0" r={medidas.raioDoOlho} />
      </g>
    </g>
  );
}
