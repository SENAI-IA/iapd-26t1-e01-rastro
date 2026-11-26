import { useLayoutEffect, useRef } from "react";
import "./DicaDoTermo.css";

interface Props {
  id: string;
  titulo: string;
  definicao: string;
  ancora: HTMLElement | null;
  aberta: boolean;
}

const MARGEM = 8;

export default function DicaDoTermo({ id, titulo, definicao, ancora, aberta }: Props) {
  const dica = useRef<HTMLSpanElement>(null);

  useLayoutEffect(() => {
    const elemento = dica.current;
    if (!elemento || !ancora || !aberta) {
      return;
    }
    const posicionar = () => posicionarJuntoDe(elemento, ancora);
    elemento.showPopover();
    posicionar();
    window.addEventListener("scroll", posicionar, true);
    window.addEventListener("resize", posicionar);
    return () => {
      window.removeEventListener("scroll", posicionar, true);
      window.removeEventListener("resize", posicionar);
      elemento.hidePopover();
    };
  }, [ancora, aberta]);

  return (
    <span ref={dica} id={id} className="dica-do-termo" role="tooltip" popover="manual">
      <span className="dica-do-termo__titulo">{titulo}</span>
      {definicao}
    </span>
  );
}

function posicionarJuntoDe(dica: HTMLElement, ancora: HTMLElement) {
  const termo = ancora.getBoundingClientRect();
  const larguraMaxima = window.innerWidth - dica.offsetWidth - MARGEM;
  const acima = termo.top - dica.offsetHeight - MARGEM;
  dica.style.left = `${Math.max(MARGEM, Math.min(termo.left, larguraMaxima))}px`;
  dica.style.top = `${acima >= MARGEM ? acima : termo.bottom + MARGEM}px`;
}
