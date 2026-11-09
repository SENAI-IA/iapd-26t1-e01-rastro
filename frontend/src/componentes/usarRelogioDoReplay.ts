import { useEffect, useRef, useState } from "react";

export interface RelogioDoReplay {
  tempo: number;
  tocando: boolean;
  tocar: () => void;
  pausar: () => void;
  irPara: (tempo: number) => void;
}

function prefereMenosMovimento(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function usarRelogioDoReplay(duracao: number): RelogioDoReplay {
  const [tempo, setTempo] = useState(() => (prefereMenosMovimento() ? duracao : 0));
  const [tocando, setTocando] = useState(() => !prefereMenosMovimento());
  const quadroAnterior = useRef<number | null>(null);

  useEffect(() => {
    if (!tocando) {
      quadroAnterior.current = null;
      return;
    }
    let quadro = 0;
    const avancar = (agora: number) => {
      const passou = agora - (quadroAnterior.current ?? agora);
      quadroAnterior.current = agora;
      setTempo((atual) => Math.min(duracao, atual + passou));
      quadro = requestAnimationFrame(avancar);
    };
    quadro = requestAnimationFrame(avancar);
    return () => cancelAnimationFrame(quadro);
  }, [tocando, duracao]);

  useEffect(() => {
    if (tempo >= duracao) {
      setTocando(false);
    }
  }, [tempo, duracao]);

  return {
    tempo,
    tocando,
    tocar: () => {
      if (tempo >= duracao) {
        setTempo(0);
      }
      setTocando(true);
    },
    pausar: () => setTocando(false),
    irPara: (novoTempo) => {
      setTocando(false);
      setTempo(Math.max(0, Math.min(duracao, novoTempo)));
    },
  };
}
