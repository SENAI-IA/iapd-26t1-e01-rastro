import { useEffect, useRef } from "react";
import type { Acao } from "../../relatorio/tiposDoRelatorio.ts";
import AcoesDaCopia from "./AcoesDaCopia.tsx";
import Icone from "../../basicos/Icone.tsx";
import { usarCopiaDoTexto } from "../../hooks/usarCopiaDoTexto.ts";
import { usarJanelaModal } from "../../hooks/usarJanelaModal.ts";
import "./JanelaDaTarefa.css";

interface Props {
  acao: Acao;
  aoFechar: () => void;
}

export default function JanelaDaTarefa({ acao, aoFechar }: Props) {
  const { janela, fechar, fecharAoClicarFora } = usarJanelaModal();
  const caixaDeTexto = useRef<HTMLTextAreaElement>(null);
  const botaoCopiar = useRef<HTMLButtonElement>(null);
  const { estadoDaCopia, copiar } = usarCopiaDoTexto(acao.texto_task, caixaDeTexto);

  useEffect(() => {
    botaoCopiar.current?.focus();
  }, []);

  return (
    <dialog
      ref={janela}
      className="janela-da-tarefa"
      aria-labelledby="janela-da-tarefa-titulo"
      onClose={aoFechar}
      onClick={fecharAoClicarFora}
    >
      <div className="janela-da-tarefa__conteudo">
        <header className="janela-da-tarefa__cabecalho">
          <div>
            <span className="janela-da-tarefa__rotulo">Task para o board</span>
            <h2 id="janela-da-tarefa-titulo">{acao.o_que_fazer}</h2>
          </div>
          <button type="button" className="janela-da-tarefa__fechar" onClick={fechar} aria-label="Fechar a task">
            <Icone nome="fechar" tamanho={16} />
          </button>
        </header>
        <label htmlFor="janela-da-tarefa-texto" className="janela-da-tarefa__explicacao">
          Título e descrição em Markdown, prontos para colar no Azure DevOps ou no GitLab.
        </label>
        <textarea
          ref={caixaDeTexto}
          id="janela-da-tarefa-texto"
          className="janela-da-tarefa__texto"
          value={acao.texto_task}
          readOnly
          spellCheck={false}
        />
        <AcoesDaCopia estadoDaCopia={estadoDaCopia} botaoCopiar={botaoCopiar} aoCopiar={copiar} />
      </div>
    </dialog>
  );
}
