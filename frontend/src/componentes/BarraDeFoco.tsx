import { useEffect, useRef } from "react";
import { ZONAS, type NomeDaZona } from "../dados/zonas.ts";
import Icone from "./Icone.tsx";
import "./BarraDeFoco.css";

interface Props {
  zonaEmFoco: NomeDaZona;
  aoTrocarZona: (zona: NomeDaZona) => void;
  aoSair: () => void;
}

export default function BarraDeFoco({ zonaEmFoco, aoTrocarZona, aoSair }: Props) {
  const botaoDaZonaEmFoco = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    botaoDaZonaEmFoco.current?.focus();
  }, []);

  return (
    <nav className="barra-de-foco" aria-label="Modo foco">
      <div className="barra-de-foco__conteudo">
        <span className="barra-de-foco__rotulo">
          <Icone nome="alvo" />
          <span className="barra-de-foco__rotulo-texto">Foco</span>
        </span>
        <ul className="barra-de-foco__zonas">
          {ZONAS.map((zona) => {
            const emFoco = zona.id === zonaEmFoco;
            return (
              <li key={zona.id}>
                <button
                  type="button"
                  ref={emFoco ? botaoDaZonaEmFoco : undefined}
                  className="barra-de-foco__zona"
                  aria-pressed={emFoco}
                  onClick={() => aoTrocarZona(zona.id)}
                >
                  {zona.nome}
                </button>
              </li>
            );
          })}
        </ul>
        <button type="button" className="barra-de-foco__sair" onClick={aoSair}>
          <Icone nome="fechar" />
          Sair do foco
          <kbd>Esc</kbd>
        </button>
      </div>
    </nav>
  );
}
