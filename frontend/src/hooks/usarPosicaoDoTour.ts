import { useCallback, useEffect, useLayoutEffect, useState, type RefObject } from "react";
import type { PassoDoTour } from "../conteudo/tour.ts";
import { posicaoDoBalao, retanguloDoDestaque, rolagemParaMostrar, type PosicaoNaTela, type Retangulo } from "../calculosDeTela/posicaoDoTour.ts";
import { prefereMenosMovimento } from "../calculosDeTela/movimento.ts";

export interface PosicaoDoTour {
  destaque: Retangulo;
  balao: PosicaoNaTela;
}

function retanguloDe(elemento: Element): Retangulo {
  const caixa = elemento.getBoundingClientRect();
  return { topo: caixa.top, esquerda: caixa.left, largura: caixa.width, altura: caixa.height };
}

function tamanhoDaTela() {
  return { largura: document.documentElement.clientWidth, altura: window.innerHeight };
}

function rolarAteOAlvo(seletor: string, alturaDoCabecalhoFixo: number) {
  const alvo = document.querySelector(seletor);
  if (alvo) {
    const destino = rolagemParaMostrar(retanguloDe(alvo), window.scrollY, tamanhoDaTela(), alturaDoCabecalhoFixo);
    window.scrollTo({ top: destino, behavior: prefereMenosMovimento() ? "auto" : "smooth" });
  }
}

export function usarPosicaoDoTour(
  passo: PassoDoTour,
  cabecalhoFixo: HTMLElement | null,
  balao: RefObject<HTMLDivElement | null>,
): PosicaoDoTour | null {
  const [posicao, setPosicao] = useState<PosicaoDoTour | null>(null);

  const medir = useCallback(() => {
    const alvo = document.querySelector(passo.seletor);
    if (!alvo || !balao.current) {
      return;
    }
    const tela = tamanhoDaTela();
    const alturaDoCabecalhoFixo = cabecalhoFixo?.offsetHeight ?? 0;
    const destaque = retanguloDoDestaque(retanguloDe(alvo), tela, alturaDoCabecalhoFixo);
    const tamanhoDoBalao = { largura: balao.current.offsetWidth, altura: balao.current.offsetHeight };
    setPosicao({ destaque, balao: posicaoDoBalao(destaque, tamanhoDoBalao, tela, alturaDoCabecalhoFixo) });
  }, [passo, cabecalhoFixo, balao]);

  useLayoutEffect(() => {
    rolarAteOAlvo(passo.seletor, cabecalhoFixo?.offsetHeight ?? 0);
    medir();
  }, [passo, cabecalhoFixo, medir]);

  useEffect(() => {
    window.addEventListener("scroll", medir, { passive: true });
    window.addEventListener("resize", medir);
    return () => {
      window.removeEventListener("scroll", medir);
      window.removeEventListener("resize", medir);
    };
  }, [medir]);

  return posicao;
}
