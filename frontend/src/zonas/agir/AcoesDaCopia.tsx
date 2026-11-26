import type { Ref } from "react";
import Icone from "../../basicos/Icone.tsx";
import type { EstadoDaCopia } from "../../hooks/usarCopiaDoTexto.ts";

const TEXTO_DO_BOTAO: Record<EstadoDaCopia, string> = {
  pronta: "Copiar task",
  copiada: "Copiada",
  selecionada: "Texto selecionado: use Ctrl + C",
};

interface Props {
  estadoDaCopia: EstadoDaCopia;
  botaoCopiar: Ref<HTMLButtonElement>;
  aoCopiar: () => void;
}

export default function AcoesDaCopia({ estadoDaCopia, botaoCopiar, aoCopiar }: Props) {
  return (
    <div className="modal-task__acoes">
      <button
        type="button"
        className={`modal-task__copiar modal-task__copiar--${estadoDaCopia}`}
        ref={botaoCopiar}
        onClick={aoCopiar}
      >
        {estadoDaCopia === "copiada" && <Icone nome="certo" tamanho={14} />}
        {TEXTO_DO_BOTAO[estadoDaCopia]}
      </button>
      <span className="modal-task__aviso" role="status">
        {estadoDaCopia === "copiada" ? "Task copiada para a área de transferência." : ""}
      </span>
    </div>
  );
}
