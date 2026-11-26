import { useState, type RefObject } from "react";

export type EstadoDaCopia = "pronta" | "copiada" | "selecionada";

export function usarCopiaDoTexto(texto: string, campo: RefObject<HTMLTextAreaElement | null>) {
  const [estadoDaCopia, setEstadoDaCopia] = useState<EstadoDaCopia>("pronta");

  const selecionarTexto = () => {
    campo.current?.focus();
    campo.current?.select();
    setEstadoDaCopia("selecionada");
  };

  const copiar = () => {
    if (!navigator.clipboard) {
      selecionarTexto();
      return;
    }
    navigator.clipboard.writeText(texto).then(() => setEstadoDaCopia("copiada"), selecionarTexto);
  };

  return { estadoDaCopia, copiar };
}
