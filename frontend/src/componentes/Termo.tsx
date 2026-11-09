import { useId, useState, type KeyboardEvent, type MouseEvent, type ReactNode } from "react";
import { glossario, type NomeDoTermo } from "../dados/glossario.ts";
import Dica from "./Dica.tsx";
import "./Termo.css";

interface Props {
  nome: NomeDoTermo;
  children?: ReactNode;
}

export default function Termo({ nome, children }: Props) {
  const idDaDica = useId();
  const [termo, setTermo] = useState<HTMLSpanElement | null>(null);
  const [sobOPonteiro, setSobOPonteiro] = useState(false);
  const [comFoco, setComFoco] = useState(false);

  const fecharComEsc = (evento: KeyboardEvent) => {
    if (evento.key === "Escape" && (sobOPonteiro || comFoco)) {
      evento.preventDefault();
      setSobOPonteiro(false);
      setComFoco(false);
    }
  };

  const focarAoTocar = (evento: MouseEvent<HTMLSpanElement>) => {
    evento.preventDefault();
    evento.stopPropagation();
    evento.currentTarget.focus();
    setComFoco(true);
  };

  return (
    <>
      <span
        ref={setTermo}
        className="termo"
        tabIndex={0}
        aria-describedby={idDaDica}
        onPointerEnter={() => setSobOPonteiro(true)}
        onPointerLeave={() => setSobOPonteiro(false)}
        onFocus={() => setComFoco(true)}
        onBlur={() => setComFoco(false)}
        onClick={focarAoTocar}
        onKeyDown={fecharComEsc}
      >
        {children ?? nome}
      </span>
      <Dica id={idDaDica} titulo={nome} definicao={glossario[nome]} ancora={termo} aberta={sobOPonteiro || comFoco} />
    </>
  );
}
