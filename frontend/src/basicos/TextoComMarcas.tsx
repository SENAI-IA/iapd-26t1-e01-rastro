import type { ReactNode } from "react";

const NEGRITO_OU_CODIGO = /(\*\*[^*]+\*\*|`[^`]+`)/;

interface Props {
  texto: string;
}

function desenharParte(parte: string, indice: number): ReactNode {
  if (parte.startsWith("**")) {
    return <strong key={indice}>{parte.slice(2, -2)}</strong>;
  }
  if (parte.startsWith("`")) {
    return <code key={indice}>{parte.slice(1, -1)}</code>;
  }
  return parte;
}

export default function TextoComMarcas({ texto }: Props) {
  return <>{texto.split(NEGRITO_OU_CODIGO).map(desenharParte)}</>;
}
