import { useEffect, useState, useSyncExternalStore } from "react";
import type { Tema } from "../telas/tiposDaTela.ts";

const CONSULTA_DO_ESCURO = "(prefers-color-scheme: dark)";

function temaDoSistema(): Tema {
  return window.matchMedia(CONSULTA_DO_ESCURO).matches ? "escuro" : "claro";
}

function ouvirTemaDoSistema(aoMudar: () => void) {
  const consulta = window.matchMedia(CONSULTA_DO_ESCURO);
  consulta.addEventListener("change", aoMudar);
  return () => consulta.removeEventListener("change", aoMudar);
}

export function usarTema() {
  const [temaEscolhido, setTemaEscolhido] = useState<Tema | null>(null);
  const sistema = useSyncExternalStore(ouvirTemaDoSistema, temaDoSistema);
  const tema = temaEscolhido ?? sistema;

  useEffect(() => {
    if (temaEscolhido) {
      document.documentElement.dataset.tema = temaEscolhido;
    }
  }, [temaEscolhido]);

  const trocarTema = () => setTemaEscolhido(tema === "claro" ? "escuro" : "claro");

  return { tema, trocarTema };
}
