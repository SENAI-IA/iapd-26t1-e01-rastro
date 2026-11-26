type TamanhoDoCursor = "grande" | "medio" | "pequeno";

const CONTORNO_DO_CURSOR: Record<TamanhoDoCursor, string> = {
  grande: "l0 18 l5 -5 l4 8 l3 -1.5 l-4 -8 l7 0 z",
  medio: "l0 16 l4.5 -4.5 l3.5 7 l2.7 -1.3 l-3.5 -7 l6.3 0 z",
  pequeno: "l0 12 l3.4 -3.4 l2.6 5.2 l2 -1 l-2.6 -5.2 l4.8 0 z",
};

interface Props {
  x: number;
  y: number;
  tamanho: TamanhoDoCursor;
  animacao: string;
}

export default function Cursor({ x, y, tamanho, animacao }: Props) {
  const prefixo = tamanho === "pequeno" ? "modo-anim" : "ilustracao";
  return (
    <path
      className={`${prefixo}__traco ${prefixo}__traco--destaque ${animacao}`}
      d={`M${x} ${y} ${CONTORNO_DO_CURSOR[tamanho]}`}
    />
  );
}
