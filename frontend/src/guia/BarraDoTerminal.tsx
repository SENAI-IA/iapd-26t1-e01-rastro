import type { ReactNode } from "react";

interface Props {
  titulo: string;
  children: ReactNode;
}

export default function BarraDoTerminal({ titulo, children }: Props) {
  return (
    <div className="terminal-do-passo__barra">
      <span className="terminal-do-passo__bolinhas" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      <span className="terminal-do-passo__titulo">{titulo}</span>
      {children}
    </div>
  );
}
