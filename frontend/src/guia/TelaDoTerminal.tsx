import { useEffect, useRef } from "react";
import type { LinhaNaTela } from "../calculosDeTela/quadrosDoTerminal.ts";

interface Props {
  tela: LinhaNaTela[];
  aoVivo: boolean;
  ocupado?: boolean;
}

function chaveDoPedaco(indice: number, texto: string): string {
  return `${indice}-${texto}`;
}

export default function TelaDoTerminal({ tela, aoVivo, ocupado = false }: Props) {
  const elemento = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (aoVivo && elemento.current) {
      elemento.current.scrollTop = elemento.current.scrollHeight;
    }
  }, [tela, aoVivo]);

  return (
    <div
      ref={elemento}
      className={aoVivo ? "terminal-do-passo__tela terminal-do-passo__tela--ao-vivo" : "terminal-do-passo__tela"}
      role={aoVivo ? "log" : undefined}
      aria-label={aoVivo ? "Saída simulada do terminal" : undefined}
      aria-busy={aoVivo ? ocupado : undefined}
      aria-hidden={aoVivo ? undefined : true}
    >
      {tela.map((linha, indiceDaLinha) => (
        <div key={indiceDaLinha}>
          {linha.pedacos.map((pedaco, indice) => (
            <span key={chaveDoPedaco(indice, pedaco.texto)} className={pedaco.tom ? `terminal-do-passo__${pedaco.tom}` : undefined}>
              {pedaco.texto}
            </span>
          ))}
          {linha.cursor && <span className="terminal-do-passo__cursor" />}
        </div>
      ))}
    </div>
  );
}
