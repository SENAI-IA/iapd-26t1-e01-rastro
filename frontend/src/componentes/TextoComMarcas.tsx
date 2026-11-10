import type { ReactNode } from "react";

const MARCAS = /(\*\*[^*]+\*\*|`[^`]+`)/;

interface Props {
  texto: string;
}

function trecho(parte: string, indice: number): ReactNode {
  if (parte.startsWith("**")) {
    return <strong key={indice}>{parte.slice(2, -2)}</strong>;
  }
  if (parte.startsWith("`")) {
    return <code key={indice}>{parte.slice(1, -1)}</code>;
  }
  return parte;
}

export default function TextoComMarcas({ texto }: Props) {
  return <>{texto.split(MARCAS).map(trecho)}</>;
}
