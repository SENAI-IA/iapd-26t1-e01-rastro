import { useEffect, useMemo, useState } from "react";
import type { LinhaDaSimulacao } from "../conteudo/simulacoesDoGuia.ts";
import { prefereMenosMovimento } from "../calculosDeTela/movimento.ts";
import { quadrosDoTerminal } from "../calculosDeTela/quadrosDoTerminal.ts";

export function usarSimulacaoDoTerminal(linhas: LinhaDaSimulacao[]) {
  const quadros = useMemo(() => quadrosDoTerminal(linhas), [linhas]);
  const ultimo = quadros.length - 1;
  const primeiro = prefereMenosMovimento() ? ultimo : 0;
  const [indice, setIndice] = useState(primeiro);

  useEffect(() => {
    if (indice >= ultimo) {
      return;
    }
    const proximo = window.setTimeout(() => setIndice(indice + 1), quadros[indice + 1].esperaAntes);
    return () => window.clearTimeout(proximo);
  }, [indice, ultimo, quadros]);

  return {
    tela: quadros[indice].tela,
    terminou: indice >= ultimo,
    recomecar: () => setIndice(primeiro),
  };
}
