import { useRef, useState, type KeyboardEvent } from "react";
import type { PassoDoTour } from "../conteudo/tour.ts";
import BalaoDoTour from "./BalaoDoTour.tsx";
import { usarJanelaModal } from "../hooks/usarJanelaModal.ts";
import { usarPosicaoDoTour } from "../hooks/usarPosicaoDoTour.ts";
import "./TourGuiado.css";

interface Props {
  passos: PassoDoTour[];
  topo: HTMLElement | null;
  aoFechar: () => void;
}

function andarPelasSetas(avancar: () => void, voltar: () => void) {
  return (evento: KeyboardEvent<HTMLDialogElement>) => {
    if (evento.key === "ArrowRight") {
      evento.preventDefault();
      avancar();
    } else if (evento.key === "ArrowLeft") {
      evento.preventDefault();
      voltar();
    }
  };
}

export default function TourGuiado({ passos, topo, aoFechar }: Props) {
  const { janela, fechar, fecharAoClicarFora } = usarJanelaModal();
  const balao = useRef<HTMLDivElement>(null);
  const [indice, setIndice] = useState(0);
  const posicao = usarPosicaoDoTour(passos[indice], topo, balao);

  const avancar = () => {
    if (indice === passos.length - 1) {
      fechar();
      return;
    }
    setIndice(indice + 1);
  };

  const voltar = () => {
    if (indice > 0) {
      setIndice(indice - 1);
    }
  };

  return (
    <dialog
      ref={janela}
      className="tour"
      aria-labelledby="tour-titulo"
      onClose={aoFechar}
      onClick={fecharAoClicarFora}
      onKeyDown={andarPelasSetas(avancar, voltar)}
    >
      {posicao && (
        <div
          className="tour__destaque"
          style={{
            top: posicao.destaque.topo,
            left: posicao.destaque.esquerda,
            width: posicao.destaque.largura,
            height: posicao.destaque.altura,
          }}
        />
      )}
      <BalaoDoTour
        ref={balao}
        key={indice}
        passo={passos[indice]}
        numero={indice + 1}
        total={passos.length}
        posicao={posicao?.balao ?? null}
        aoPular={fechar}
        aoAvancar={avancar}
        aoVoltar={voltar}
      />
    </dialog>
  );
}
