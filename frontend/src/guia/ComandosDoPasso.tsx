import { useState } from "react";
import type { Comando } from "../conteudo/guia.ts";

interface Props {
  comandos: Comando[];
}

export default function ComandosDoPasso({ comandos }: Props) {
  const [copiado, setCopiado] = useState<string | null>(null);

  const copiar = (comando: Comando) => {
    navigator.clipboard?.writeText(comando.texto).then(
      () => setCopiado(comando.sistema),
      () => setCopiado(null),
    );
  };

  return (
    <>
      {comandos.map((comando) => (
        <div key={comando.sistema} className="passo-do-guia__comando">
          <span className="passo-do-guia__sistema">{comando.sistema}</span>
          <code>{comando.texto}</code>
          <button
            type="button"
            className="passo-do-guia__copiar"
            onClick={() => copiar(comando)}
            aria-label={`Copiar o comando para ${comando.sistema}`}
          >
            {copiado === comando.sistema ? "Copiado" : "Copiar"}
          </button>
        </div>
      ))}
    </>
  );
}
