import { useEffect, useRef, type Ref } from "react";
import type { PassoDoTour } from "../conteudo/tour.ts";
import type { Ponto } from "../calculosDeTela/posicaoDoTour.ts";
import TermosDoPasso from "./TermosDoPasso.tsx";

interface Props {
  ref: Ref<HTMLDivElement>;
  passo: PassoDoTour;
  numero: number;
  total: number;
  posicao: Ponto | null;
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
      className={posicao ? "tour__balao" : "tour__balao tour__balao--medindo"}
      style={posicao ? { top: posicao.topo, left: posicao.esquerda } : undefined}
    >
      <span className="tour__passo">
        {numero} de {total}
      </span>
      <h2 id="tour-titulo" className="tour__titulo">
        {passo.titulo}
      </h2>
      <p className="tour__texto">{passo.texto}</p>
      {passo.termos && <TermosDoPasso termos={passo.termos} />}
      <div className="tour__acoes">
        <button type="button" className="tour__pular" onClick={aoPular}>
          {ultimo ? "Fechar" : "Pular"}
        </button>
        <div className="tour__navegacao">
          {numero > 1 && (
            <button type="button" className="tour__botao tour__botao--secundario" onClick={aoVoltar}>
              Voltar
            </button>
          )}
          <button type="button" className="tour__botao" ref={botaoProximo} onClick={aoAvancar}>
            {ultimo ? "Concluir" : "Próximo"}
          </button>
        </div>
      </div>
    </div>
  );
}
