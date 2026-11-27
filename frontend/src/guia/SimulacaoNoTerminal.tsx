import { useEffect, useRef } from "react";
import type { LinhaDaSimulacao } from "../conteudo/simulacoesDoGuia.ts";
import Icone from "../basicos/Icone.tsx";
import { usarSimulacaoDoTerminal } from "../hooks/usarSimulacaoDoTerminal.ts";
import BarraDoTerminal from "./BarraDoTerminal.tsx";
import TelaDoTerminal from "./TelaDoTerminal.tsx";

interface Props {
  linhas: LinhaDaSimulacao[];
  aoFechar: () => void;
}

export default function SimulacaoNoTerminal({ linhas, aoFechar }: Props) {
  const simulacao = usarSimulacaoDoTerminal(linhas);
  const botaoDeRecomecar = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    botaoDeRecomecar.current?.focus({ preventScroll: true });
  }, []);

  return (
    <div className="terminal-do-passo terminal-do-passo--ao-vivo">
      <BarraDoTerminal titulo="Simulação num site de exemplo">
        <button
          ref={botaoDeRecomecar}
          type="button"
          className="terminal-do-passo__acao"
          onClick={simulacao.recomecar}
          aria-label="Simular de novo"
          title="Simular de novo"
        >
          <Icone nome="reiniciar" tamanho={14} />
        </button>
        <button type="button" className="terminal-do-passo__acao" onClick={aoFechar} aria-label="Fechar a simulação" title="Fechar a simulação">
          <Icone nome="fechar" tamanho={14} />
        </button>
      </BarraDoTerminal>
      <TelaDoTerminal tela={simulacao.tela} aoVivo ocupado={!simulacao.terminou} />
    </div>
  );
}
