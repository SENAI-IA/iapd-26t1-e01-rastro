import { useEffect, useRef, useState, type RefObject } from "react";
import type { NomeDaZona } from "../conteudo/zonas.ts";
import { idDaZona } from "../calculosDeTela/identificadores.ts";
import { rolarAteOElemento } from "../calculosDeTela/rolagem.ts";

function algumDialogoAberto(): boolean {
  return document.querySelector("dialog[open]") !== null;
}

function rolarAteAZona(zona: NomeDaZona, cabecalhoFixo: HTMLElement | null) {
  const elemento = document.getElementById(idDaZona(zona));
  if (!elemento) {
    return;
  }
  rolarAteOElemento(elemento, cabecalhoFixo?.offsetHeight ?? 0);
  elemento.querySelector<HTMLButtonElement>(".zona-do-painel__focar")?.focus({ preventScroll: true });
}

export function usarModoFoco(cabecalhoFixo: RefObject<HTMLElement | null>) {
  const [zonaEmFoco, setZonaEmFoco] = useState<NomeDaZona | null>(null);
  const zonaQueSaiuDoFoco = useRef<NomeDaZona | null>(null);

  useEffect(() => {
    if (zonaEmFoco !== null) {
      window.scrollTo({ top: 0 });
      return;
    }
    if (zonaQueSaiuDoFoco.current) {
      rolarAteAZona(zonaQueSaiuDoFoco.current, cabecalhoFixo.current);
      zonaQueSaiuDoFoco.current = null;
    }
  }, [zonaEmFoco, cabecalhoFixo]);

  useEffect(() => {
    if (zonaEmFoco === null) {
      return;
    }
    const sairComEsc = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !evento.defaultPrevented && !algumDialogoAberto()) {
        zonaQueSaiuDoFoco.current = zonaEmFoco;
        setZonaEmFoco(null);
      }
    };
    document.addEventListener("keydown", sairComEsc);
    return () => document.removeEventListener("keydown", sairComEsc);
  }, [zonaEmFoco]);

  const entrarNoFoco = (zona: NomeDaZona) => setZonaEmFoco(zona);

  const sairDoFoco = () => {
    zonaQueSaiuDoFoco.current = zonaEmFoco;
    setZonaEmFoco(null);
  };

  const sairDoFocoSemVoltarAZona = () => setZonaEmFoco(null);

  return { zonaEmFoco, entrarNoFoco, sairDoFoco, sairDoFocoSemVoltarAZona };
}
