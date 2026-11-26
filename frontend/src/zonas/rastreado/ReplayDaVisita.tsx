import { useRef, useState, type CSSProperties } from "react";
import type { Biblioteca, PassoDaVisita } from "../../relatorio/tiposDoRelatorio.ts";
import { listarChegadas } from "../../calculosDeTela/chegadasDaVisita.ts";
import {
  duracaoDaVisita,
  duracaoDoReplay,
  progressoDoReplay,
  requisicoesQueChegaram,
} from "../../calculosDeTela/progressoDoReplay.ts";
import ContagemDoReplay from "./ContagemDoReplay.tsx";
import ControlesDoReplay from "./ControlesDoReplay.tsx";
import LegendaDoReplay from "./LegendaDoReplay.tsx";
import MancheteDoReplay from "./MancheteDoReplay.tsx";
import RadarDaVisita from "./RadarDaVisita.tsx";
import Termo from "../../basicos/Termo.tsx";
import { usarAlturaAteADobra } from "../../hooks/usarAlturaAteADobra.ts";
import { usarRelogioDoReplay } from "../../hooks/usarRelogioDoReplay.ts";
import "./ReplayDaVisita.css";

interface Props {
  passos: PassoDaVisita[];
  bibliotecas: Biblioteca[];
  aoIrParaBiblioteca: (id: string) => void;
}

export default function ReplayDaVisita({ passos, bibliotecas, aoIrParaBiblioteca }: Props) {
  const replay = duracaoDoReplay(passos.length);
  const relogio = usarRelogioDoReplay(replay);
  const progresso = progressoDoReplay(relogio.tempo, replay, passos.length);
  const [bibliotecaEmDestaque, setBibliotecaEmDestaque] = useState<string | null>(null);
  const chegadas = listarChegadas(passos, bibliotecas);
  const chegaram = requisicoesQueChegaram(progresso, passos.length);
  const falhasQueChegaram = chegadas.filter((chegada) => chegada.ordem < progresso);
  const terminou = relogio.tempo >= replay;
  const painel = useRef<HTMLDivElement>(null);
  const alturaDoPalco = usarAlturaAteADobra(painel);

  return (
    <section className="replay" aria-labelledby="replay-titulo">
      <div className="replay__painel" ref={painel}>
        <div className="replay__lado">
          <div className="replay__cabecalho">
            <h2 id="replay-titulo">A visita, de novo</h2>
            <p>
              O Rastro refaz a visita do <Termo nome="HAR" />, arquivo por arquivo. Clique numa biblioteca para ver
              as falhas.
            </p>
          </div>
          <p className="replay__manchete" aria-live="polite">
            <MancheteDoReplay chegaram={chegaram} total={passos.length} falhas={terminou ? chegadas : falhasQueChegaram} />
          </p>
          <ContagemDoReplay
            arquivos={chegaram}
            totalDeArquivos={passos.length}
            falhas={falhasQueChegaram.length}
            totalDeFalhas={chegadas.length}
          />
          <ControlesDoReplay relogio={relogio} duracaoDoReplay={replay} duracaoDaVisita={duracaoDaVisita(passos)} />
          <LegendaDoReplay />
        </div>
        <div
          className="replay__palco"
          style={alturaDoPalco === null ? undefined : ({ "--altura-do-palco": `${alturaDoPalco}px` } as CSSProperties)}
        >
          <RadarDaVisita
            passos={passos}
            chegadas={chegadas}
            progresso={progresso}
            bibliotecaEmDestaque={bibliotecaEmDestaque}
            aoEscolherBiblioteca={aoIrParaBiblioteca}
            aoDestacarBiblioteca={setBibliotecaEmDestaque}
          />
        </div>
      </div>
    </section>
  );
}
