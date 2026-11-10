import { useCallback, useEffect, useLayoutEffect, useRef, useState, type KeyboardEvent, type MouseEvent } from "react";
import { glossario } from "../dados/glossario.ts";
import type { PassoDoTour } from "../dados/tour.ts";
import { posicaoDoBalao, retanguloDoDestaque, rolagemParaMostrar, type Ponto, type Retangulo } from "./posicaoDoTour.ts";
import "./TourGuiado.css";

interface Props {
  passos: PassoDoTour[];
  topo: HTMLElement | null;
  aoFechar: () => void;
}

interface Medida {
  destaque: Retangulo;
  balao: Ponto;
}

function retanguloDe(elemento: Element): Retangulo {
  const caixa = elemento.getBoundingClientRect();
  return { topo: caixa.top, esquerda: caixa.left, largura: caixa.width, altura: caixa.height };
}

function telaAtual() {
  return { largura: document.documentElement.clientWidth, altura: window.innerHeight };
}

function preferePoucoMovimento(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export default function TourGuiado({ passos, topo, aoFechar }: Props) {
  const modal = useRef<HTMLDialogElement>(null);
  const balao = useRef<HTMLDivElement>(null);
  const botaoProximo = useRef<HTMLButtonElement>(null);
  const [indice, setIndice] = useState(0);
  const [medida, setMedida] = useState<Medida | null>(null);
  const passo = passos[indice];
  const ultimo = indice === passos.length - 1;

  const medir = useCallback(() => {
    const alvo = document.querySelector(passo.seletor);
    if (!alvo || !balao.current) {
      return;
    }
    const tela = telaAtual();
    const alturaDoTopo = topo?.offsetHeight ?? 0;
    const destaque = retanguloDoDestaque(retanguloDe(alvo), tela, alturaDoTopo);
    const tamanhoDoBalao = { largura: balao.current.offsetWidth, altura: balao.current.offsetHeight };
    setMedida({ destaque, balao: posicaoDoBalao(destaque, tamanhoDoBalao, tela, alturaDoTopo) });
  }, [passo, topo]);

  useLayoutEffect(() => {
    modal.current?.showModal();
  }, []);

  useLayoutEffect(() => {
    const alvo = document.querySelector(passo.seletor);
    if (alvo) {
      const destino = rolagemParaMostrar(retanguloDe(alvo), window.scrollY, telaAtual(), topo?.offsetHeight ?? 0);
      window.scrollTo({ top: destino, behavior: preferePoucoMovimento() ? "auto" : "smooth" });
    }
    medir();
  }, [passo, topo, medir]);

  const medido = medida !== null;
  useEffect(() => {
    if (medido) {
      botaoProximo.current?.focus();
    }
  }, [indice, medido]);

  useEffect(() => {
    window.addEventListener("scroll", medir, { passive: true });
    window.addEventListener("resize", medir);
    return () => {
      window.removeEventListener("scroll", medir);
      window.removeEventListener("resize", medir);
    };
  }, [medir]);

  const fechar = () => modal.current?.close();
  const avancar = () => (ultimo ? fechar() : setIndice(indice + 1));
  const voltar = () => indice > 0 && setIndice(indice - 1);

  const andarPelasSetas = (evento: KeyboardEvent<HTMLDialogElement>) => {
    if (evento.key === "ArrowRight") {
      evento.preventDefault();
      avancar();
    } else if (evento.key === "ArrowLeft") {
      evento.preventDefault();
      voltar();
    }
  };

  const fecharAoClicarFora = (evento: MouseEvent<HTMLDialogElement>) => {
    if (evento.target === evento.currentTarget) {
      fechar();
    }
  };

  return (
    <dialog
      ref={modal}
      className="tour"
      aria-labelledby="tour-titulo"
      onClose={aoFechar}
      onClick={fecharAoClicarFora}
      onKeyDown={andarPelasSetas}
    >
      {medida && (
        <div
          className="tour__destaque"
          style={{
            top: medida.destaque.topo,
            left: medida.destaque.esquerda,
            width: medida.destaque.largura,
            height: medida.destaque.altura,
          }}
        />
      )}
      <div
        ref={balao}
        key={indice}
        className={medida ? "tour__balao" : "tour__balao tour__balao--medindo"}
        style={medida ? { top: medida.balao.topo, left: medida.balao.esquerda } : undefined}
      >
        <span className="tour__passo">
          {indice + 1} de {passos.length}
        </span>
        <h2 id="tour-titulo" className="tour__titulo">
          {passo.titulo}
        </h2>
        <p className="tour__texto">{passo.texto}</p>
        {passo.termos && (
          <dl className="tour__termos">
            <span className="tour__rotulo">No glossário</span>
            {passo.termos.map((termo) => (
              <div key={termo}>
                <dt>{termo}</dt>
                <dd>{glossario[termo]}</dd>
              </div>
            ))}
          </dl>
        )}
        <div className="tour__acoes">
          <button type="button" className="tour__pular" onClick={fechar}>
            {ultimo ? "Fechar" : "Pular"}
          </button>
          <div className="tour__navegacao">
            {indice > 0 && (
              <button type="button" className="tour__botao tour__botao--secundario" onClick={voltar}>
                Voltar
              </button>
            )}
            <button type="button" className="tour__botao" ref={botaoProximo} onClick={avancar}>
              {ultimo ? "Concluir" : "Próximo"}
            </button>
          </div>
        </div>
      </div>
    </dialog>
  );
}
