import { useRef, useState, type KeyboardEvent } from "react";
import type { PassoDoTour } from "../conteudo/tour.ts";
import BalaoDoTour from "./BalaoDoTour.tsx";
import { usarJanelaModal } from "../hooks/usarJanelaModal.ts";
import { usarPosicaoDoTour } from "../hooks/usarPosicaoDoTour.ts";
import "./TourGuiado.css";

interface Props {
  passos: PassoDoTour[];
  cabecalhoFixo: HTMLElement | null;
  aoFechar: () => void;
}

function andarPelasSetas(avancar: () => void, voltar: () => void) {
  const acaoDaSeta: Partial<Record<string, () => void>> = { ArrowRight: avancar, ArrowLeft: voltar };
  return (evento: KeyboardEvent<HTMLDialogElement>) => {
    const acao = acaoDaSeta[evento.key];
    if (acao === undefined) {
      return;
    }
    evento.preventDefault();
    acao();
  };
}

export default function TourGuiado({ passos, cabecalhoFixo, aoFechar }: Props) {
  const { janela, fechar, fecharAoClicarFora } = usarJanelaModal();
  const balao = useRef<HTMLDivElement>(null);
  const [indice, setIndice] = useState(0);
  const posicao = usarPosicaoDoTour(passos[indice], cabecalhoFixo, balao);

  const avancar = () => {
    if (indice === passos.length - 1) {
      fechar();
      return;
    }
    setIndice(indice + 1);
  };

  const voltar = () => {
    if (indice === 0) {
      return;
    }
    setIndice(indice - 1);
  };

  return (
    <dialog
      ref={janela}
      className="tour-guiado"
      aria-labelledby="tour-guiado-titulo"
      onClose={aoFechar}
      onClick={fecharAoClicarFora}
      onKeyDown={andarPelasSetas(avancar, voltar)}
    >
      {posicao && (
        <div
          className="tour-guiado__destaque"
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
