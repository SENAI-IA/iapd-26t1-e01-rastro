import { useEffect, useRef } from "react";
import type { Acao } from "../../relatorio/tiposDoRelatorio.ts";
import AcoesDaCopia from "./AcoesDaCopia.tsx";
import Icone from "../../basicos/Icone.tsx";
import { usarCopiaDoTexto } from "../../hooks/usarCopiaDoTexto.ts";
import { usarJanelaModal } from "../../hooks/usarJanelaModal.ts";
import "./ModalTask.css";

interface Props {
  acao: Acao;
  aoFechar: () => void;
}

export default function ModalTask({ acao, aoFechar }: Props) {
  const { janela, fechar, fecharAoClicarFora } = usarJanelaModal();
  const texto = useRef<HTMLTextAreaElement>(null);
  const botaoCopiar = useRef<HTMLButtonElement>(null);
  const { estadoDaCopia, copiar } = usarCopiaDoTexto(acao.texto_task, texto);

  useEffect(() => {
    botaoCopiar.current?.focus();
  }, []);

  return (
    <dialog
      ref={janela}
      className="modal-task"
      aria-labelledby="modal-task-titulo"
      onClose={aoFechar}
      onClick={fecharAoClicarFora}
    >
      <div className="modal-task__conteudo">
        <header className="modal-task__cabecalho">
          <div>
            <span className="modal-task__rotulo">Task para o board</span>
            <h2 id="modal-task-titulo">{acao.o_que_fazer}</h2>
          </div>
          <button type="button" className="modal-task__fechar" onClick={fechar} aria-label="Fechar a task">
            <Icone nome="fechar" tamanho={16} />
          </button>
        </header>
        <label htmlFor="modal-task-texto" className="modal-task__explicacao">
          Título e descrição em Markdown, prontos para colar no Azure DevOps ou no GitLab.
        </label>
        <textarea
          ref={texto}
          id="modal-task-texto"
          className="modal-task__texto"
          value={acao.texto_task}
          readOnly
          spellCheck={false}
        />
        <AcoesDaCopia estadoDaCopia={estadoDaCopia} botaoCopiar={botaoCopiar} aoCopiar={copiar} />
      </div>
    </dialog>
  );
}
