import { useEffect, useState, type RefObject } from "react";

export function usarMenuAberto(caixa: RefObject<HTMLElement | null>) {
  const [aberto, setAberto] = useState(false);

  useEffect(() => {
    if (!aberto) {
      return;
    }
    const fecharNoCliqueFora = (evento: PointerEvent) => {
      if (evento.target instanceof Node && !caixa.current?.contains(evento.target)) {
        setAberto(false);
      }
    };
    const fecharNoEsc = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") {
        setAberto(false);
      }
    };
    document.addEventListener("pointerdown", fecharNoCliqueFora);
    document.addEventListener("keydown", fecharNoEsc);
    return () => {
      document.removeEventListener("pointerdown", fecharNoCliqueFora);
      document.removeEventListener("keydown", fecharNoEsc);
    };
  }, [aberto, caixa]);

  return {
    aberto,
    alternar: () => setAberto((atual) => !atual),
    fechar: () => setAberto(false),
  };
}
