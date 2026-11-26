import { useState } from "react";
import type { Comando } from "../conteudo/guia.ts";

interface Props {
  comandos: Comando[];
}

type ResultadoDaCopia = "copiado" | "selecionado";

interface CopiaDoComando {
  sistema: string;
  resultado: ResultadoDaCopia;
}

const TEXTO_DO_BOTAO: Record<ResultadoDaCopia, string> = {
  copiado: "Copiado",
  selecionado: "Use Ctrl + C",
};

function selecionarTexto(elemento: Element | null | undefined) {
  const selecao = window.getSelection();
  if (elemento && selecao) {
    selecao.selectAllChildren(elemento);
  }
}

export default function ComandosDoPasso({ comandos }: Props) {
  const [copia, setCopia] = useState<CopiaDoComando | null>(null);

  const copiar = (comando: Comando, botao: HTMLButtonElement) => {
    const selecionar = () => {
      selecionarTexto(botao.parentElement?.querySelector("code"));
      setCopia({ sistema: comando.sistema, resultado: "selecionado" });
    };
    if (!navigator.clipboard) {
      selecionar();
      return;
    }
    navigator.clipboard.writeText(comando.texto).then(
      () => setCopia({ sistema: comando.sistema, resultado: "copiado" }),
      selecionar,
    );
  };

  const textoDoBotao = (comando: Comando) =>
    copia?.sistema === comando.sistema ? TEXTO_DO_BOTAO[copia.resultado] : "Copiar";

  return (
    <>
      {comandos.map((comando) => (
        <div key={comando.sistema} className="passo-do-guia__comando">
          <span className="passo-do-guia__sistema">{comando.sistema}</span>
          <code>{comando.texto}</code>
          <button
            type="button"
            className="passo-do-guia__copiar"
            onClick={(evento) => copiar(comando, evento.currentTarget)}
            aria-label={`Copiar o comando para ${comando.sistema}`}
          >
            {textoDoBotao(comando)}
          </button>
        </div>
      ))}
    </>
  );
}
