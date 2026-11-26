import { useLayoutEffect, useRef, type MouseEvent } from "react";

export function usarJanelaModal() {
  const janela = useRef<HTMLDialogElement>(null);

  useLayoutEffect(() => {
    janela.current?.showModal();
  }, []);

  const fechar = () => janela.current?.close();

  const fecharAoClicarFora = (evento: MouseEvent<HTMLDialogElement>) => {
    if (evento.target === evento.currentTarget) {
      fechar();
    }
  };

  return { janela, fechar, fecharAoClicarFora };
}
