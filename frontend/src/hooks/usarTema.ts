import { useEffect, useState } from "react";
import type { Tema } from "../telas/tiposDaTela.ts";

function temaDoSistema(): Tema {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "escuro" : "claro";
}

export function usarTema() {
  const [temaEscolhido, setTemaEscolhido] = useState<Tema | null>(null);
  const tema = temaEscolhido ?? temaDoSistema();

  useEffect(() => {
    if (temaEscolhido) {
      document.documentElement.dataset.tema = temaEscolhido;
    }
  }, [temaEscolhido]);

  const trocarTema = () => setTemaEscolhido(tema === "claro" ? "escuro" : "claro");

  return { tema, trocarTema };
}
