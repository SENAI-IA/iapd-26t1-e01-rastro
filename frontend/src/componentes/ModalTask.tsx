import { useEffect, useRef, useState, type MouseEvent } from "react";
import type { Acao } from "../tipos.ts";
import Icone from "./Icone.tsx";
import "./ModalTask.css";

type EstadoDaCopia = "pronta" | "copiada" | "selecionada";

const TEXTO_DO_BOTAO: Record<EstadoDaCopia, string> = {
  pronta: "Copiar task",
  copiada: "Copiada",
  selecionada: "Texto selecionado: use Ctrl + C",
};

interface Props {
  acao: Acao;
  aoFechar: () => void;
}

export default function ModalTask({ acao, aoFechar }: Props) {
  const modal = useRef<HTMLDialogElement>(null);
  const texto = useRef<HTMLTextAreaElement>(null);
  const botaoCopiar = useRef<HTMLButtonElement>(null);
  const [estadoDaCopia, setEstadoDaCopia] = useState<EstadoDaCopia>("pronta");

  useEffect(() => {
    modal.current?.showModal();
    botaoCopiar.current?.focus();
  }, []);

  const fechar = () => modal.current?.close();
  const fecharAoClicarFora = (evento: MouseEvent<HTMLDialogElement>) => {
    if (evento.target === evento.currentTarget) {
      fechar();
    }
  };

  const selecionarTexto = () => {
    texto.current?.focus();
    texto.current?.select();
    setEstadoDaCopia("selecionada");
  };

  const copiar = () => {
    if (!navigator.clipboard) {
      selecionarTexto();
      return;
    }
    navigator.clipboard.writeText(acao.texto_task).then(() => setEstadoDaCopia("copiada"), selecionarTexto);
  };

  return (
    <dialog
      ref={modal}
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

        <div className="modal-task__acoes">
          <button
            type="button"
            className={`modal-task__copiar modal-task__copiar--${estadoDaCopia}`}
            ref={botaoCopiar}
            onClick={copiar}
          >
            {estadoDaCopia === "copiada" && <Icone nome="certo" tamanho={14} />}
            {TEXTO_DO_BOTAO[estadoDaCopia]}
          </button>
          <span className="modal-task__aviso" role="status">
            {estadoDaCopia === "copiada" ? "Task copiada para a área de transferência." : ""}
          </span>
        </div>
      </div>
    </dialog>
  );
}
