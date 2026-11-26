import { useLayoutEffect, useState, type RefObject } from "react";

const PADDING_DO_PAINEL = 36;
const FOLGA_EMBAIXO = 16;
const ALTURA_MINIMA = 320;
const LARGURA_MINIMA_LADO_A_LADO = 900;

function medirAlturaAteADobra(elemento: HTMLElement): number | null {
  if (window.innerWidth < LARGURA_MINIMA_LADO_A_LADO) {
    return null;
  }
  const topoNaPagina = elemento.getBoundingClientRect().top + window.scrollY;
  return Math.max(ALTURA_MINIMA, window.innerHeight - topoNaPagina - PADDING_DO_PAINEL - FOLGA_EMBAIXO);
}

export function usarAlturaAteADobra(referencia: RefObject<HTMLElement | null>): number | null {
  const [altura, setAltura] = useState<number | null>(null);

  useLayoutEffect(() => {
    const medir = () => {
      if (referencia.current) {
        setAltura(medirAlturaAteADobra(referencia.current));
      }
    };
    medir();
    const observador = new ResizeObserver(medir);
    observador.observe(document.body);
    window.addEventListener("resize", medir);
    return () => {
      observador.disconnect();
      window.removeEventListener("resize", medir);
    };
  }, [referencia]);

  return altura;
}
