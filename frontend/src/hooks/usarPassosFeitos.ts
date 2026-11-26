import { useState } from "react";
import { depoisDeDesenhar } from "../calculosDeTela/desenho.ts";
import { ID_DO_FIM_DO_GUIA, idDoPassoDoGuia } from "../calculosDeTela/identificadores.ts";
import { prefereMenosMovimento } from "../calculosDeTela/movimento.ts";
import { rolarAteOElemento } from "../calculosDeTela/rolagem.ts";

export interface PassosFeitos {
  feitos: Set<number>;
  alternar: (indice: number) => void;
  desmarcarTodos: () => void;
}

function proximoPassoPendente(depoisDe: number, feitos: Set<number>, total: number): number | null {
  for (let indice = depoisDe + 1; indice < total; indice++) {
    if (!feitos.has(indice)) {
      return indice;
    }
  }
  return null;
}

function idDoDestino(proximo: number | null): string {
  if (proximo === null) {
    return ID_DO_FIM_DO_GUIA;
  }
  return idDoPassoDoGuia(proximo + 1);
}

export function usarPassosFeitos(total: number, medirAlturaDoCabecalhoFixo: () => number): PassosFeitos {
  const [feitos, setFeitos] = useState<Set<number>>(new Set());

  const rolarAte = (elemento: HTMLElement) => {
    rolarAteOElemento(elemento, medirAlturaDoCabecalhoFixo(), prefereMenosMovimento() ? "auto" : "smooth");
    elemento.focus({ preventScroll: true });
  };

  const alternar = (indice: number) => {
    const novos = new Set(feitos);
    if (novos.has(indice)) {
      novos.delete(indice);
      setFeitos(novos);
      return;
    }
    novos.add(indice);
    setFeitos(novos);
    const destino = document.getElementById(idDoDestino(proximoPassoPendente(indice, novos, total)));
    if (destino) {
      depoisDeDesenhar(() => rolarAte(destino));
    }
  };

  return { feitos, alternar, desmarcarTodos: () => setFeitos(new Set()) };
}
