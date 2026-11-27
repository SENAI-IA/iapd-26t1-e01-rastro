import { useEffect, useRef } from "react";
import type { LinhaDaSimulacao } from "../conteudo/simulacoesDoGuia.ts";
import { telaParada } from "../calculosDeTela/quadrosDoTerminal.ts";
import Icone from "../basicos/Icone.tsx";
import BarraDoTerminal from "./BarraDoTerminal.tsx";
import TelaDoTerminal from "./TelaDoTerminal.tsx";

interface Props {
  linhas: LinhaDaSimulacao[];
  aoSimular: () => void;
  focarNoBotao: boolean;
}

export default function PreviaDoTerminal({ linhas, aoSimular, focarNoBotao }: Props) {
  const botaoDeSimular = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (focarNoBotao) {
      botaoDeSimular.current?.focus({ preventScroll: true });
    }
  }, [focarNoBotao]);

  return (
    <div className="terminal-do-passo terminal-do-passo--previa">
      <BarraDoTerminal titulo="Prévia">
        <button ref={botaoDeSimular} type="button" className="terminal-do-passo__simular" onClick={aoSimular} aria-label="Simular no terminal">
          <Icone nome="tocar" tamanho={13} />
          Simular
        </button>
      </BarraDoTerminal>
      <TelaDoTerminal tela={telaParada(linhas)} aoVivo={false} />
    </div>
  );
}
