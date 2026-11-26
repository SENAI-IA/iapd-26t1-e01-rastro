import { useEffect, useRef, type Ref } from "react";
import type { PassoDoTour } from "../conteudo/tour.ts";
import type { PosicaoNaTela } from "../calculosDeTela/posicaoDoTour.ts";
import TermosDoPasso from "./TermosDoPasso.tsx";

interface Props {
  ref: Ref<HTMLDivElement>;
  passo: PassoDoTour;
  numero: number;
  total: number;
  posicao: PosicaoNaTela | null;
  aoPular: () => void;
  aoAvancar: () => void;
  aoVoltar: () => void;
}

export default function BalaoDoTour({ ref, passo, numero, total, posicao, aoPular, aoAvancar, aoVoltar }: Props) {
  const botaoProximo = useRef<HTMLButtonElement>(null);
  const medido = posicao !== null;
  const ultimo = numero === total;

  useEffect(() => {
    if (medido) {
      botaoProximo.current?.focus();
    }
  }, [medido]);

  return (
    <div
      ref={ref}
      className={posicao ? "tour-guiado__balao" : "tour-guiado__balao tour-guiado__balao--medindo"}
      style={posicao ? { top: posicao.topo, left: posicao.esquerda } : undefined}
    >
      <span className="tour-guiado__passo">
        {numero} de {total}
      </span>
      <h2 id="tour-guiado-titulo" className="tour-guiado__titulo">
        {passo.titulo}
      </h2>
      <p className="tour-guiado__texto">{passo.texto}</p>
      {passo.termos && <TermosDoPasso termos={passo.termos} />}
      <div className="tour-guiado__acoes">
        <button type="button" className="tour-guiado__pular" onClick={aoPular}>
          {ultimo ? "Fechar" : "Pular"}
        </button>
        <div className="tour-guiado__navegacao">
          {numero > 1 && (
            <button type="button" className="tour-guiado__botao tour-guiado__botao--secundario" onClick={aoVoltar}>
              Voltar
            </button>
          )}
          <button type="button" className="tour-guiado__botao" ref={botaoProximo} onClick={aoAvancar}>
            {ultimo ? "Concluir" : "Próximo"}
          </button>
        </div>
      </div>
    </div>
  );
}
