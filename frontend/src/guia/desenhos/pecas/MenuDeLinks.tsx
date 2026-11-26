import { PREFIXO_DA_CLASSE, type TamanhoDaPeca } from "./tamanhoDaPeca.ts";

interface MedidasDoMenu {
  posicoes: number[];
  y: number;
  largura: number;
  altura: number;
  canto: number;
}

const MEDIDAS_DO_MENU: Record<TamanhoDaPeca, MedidasDoMenu> = {
  grande: { posicoes: [24, 92, 160], y: 46, largura: 60, altura: 16, canto: 3 },
  pequeno: { posicoes: [8, 27, 46], y: 18, largura: 16, altura: 7, canto: 1.5 },
};

interface Props {
  tamanho: TamanhoDaPeca;
}

export default function MenuDeLinks({ tamanho }: Props) {
  const medidas = MEDIDAS_DO_MENU[tamanho];
  return (
    <>
      {medidas.posicoes.map((x) => (
        <rect
          key={x}
          className={`${PREFIXO_DA_CLASSE[tamanho]}__traco`}
          x={x}
          y={medidas.y}
          width={medidas.largura}
          height={medidas.altura}
          rx={medidas.canto}
        />
      ))}
    </>
  );
}
