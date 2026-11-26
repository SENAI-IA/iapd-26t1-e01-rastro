import type { ReactNode } from "react";

interface Props {
  titulo: string;
  children: ReactNode;
}

export default function CaixaDoGuia({ titulo, children }: Props) {
  return (
    <div className="guia-como-usar__caixa">
      <h2>{titulo}</h2>
      {children}
    </div>
  );
}
