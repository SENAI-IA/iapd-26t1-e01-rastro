import { useRef, useState, type CSSProperties } from "react";
import type { Biblioteca, PassoDaVisita } from "../tipos.ts";
import { listarChegadas, type Chegada } from "./chegadasDaVisita.ts";
import { formatarDuracao } from "./formato.ts";
import Icone from "./Icone.tsx";
import RadarDaVisita from "./RadarDaVisita.tsx";
import Termo from "./Termo.tsx";
import { usarAlturaAteADobra } from "./usarAlturaAteADobra.ts";
import { usarRelogioDoReplay } from "./usarRelogioDoReplay.ts";
import "./ReplayDaVisita.css";

const REPLAY_MAIS_CURTO_MS = 5000;
const REPLAY_MAIS_LONGO_MS = 9000;
const REPLAY_POR_REQUISICAO_MS = 100;

interface Props {
  passos: PassoDaVisita[];
  bibliotecas: Biblioteca[];
  aoIrParaBiblioteca: (id: string) => void;
}

function duracaoDoReplay(requisicoes: number): number {
  return Math.min(REPLAY_MAIS_LONGO_MS, Math.max(REPLAY_MAIS_CURTO_MS, requisicoes * REPLAY_POR_REQUISICAO_MS));
}

function Manchete({ chegaram, total, falhas }: { chegaram: number; total: number; falhas: Chegada[] }) {
  if (falhas.length === 0) {
    return chegaram < total ? (
      <>Seguindo o rastro da visita…</>
    ) : (
      <>Nenhuma das {total} requisições trouxe biblioteca com falha conhecida.</>
    );
  }
  const quando = formatarDuracao((falhas.at(-1)?.inicio_ms ?? 0) / 1000);
  const quantas = falhas.length === 1 ? "1 biblioteca com falha conhecida" : `${falhas.length} bibliotecas com falha conhecida`;
  return (
    <>
      Com <strong className="replay__numero">{quando}</strong> de visita,{" "}
      <strong className="replay__numero replay__numero--alerta">{quantas}</strong>{" "}
      {falhas.length === 1 ? "já estava" : "já estavam"} no navegador de quem acessou.
    </>
  );
}

export default function ReplayDaVisita({ passos, bibliotecas, aoIrParaBiblioteca }: Props) {
  const replay = duracaoDoReplay(passos.length);
  const relogio = usarRelogioDoReplay(replay);
  const progresso = (relogio.tempo / replay) * passos.length;
  const [bibliotecaEmDestaque, setBibliotecaEmDestaque] = useState<string | null>(null);
  const chegadas = listarChegadas(passos, bibliotecas);
  const requisicoesQueChegaram = Math.min(passos.length, Math.ceil(progresso));
  const falhasQueChegaram = chegadas.filter((chegada) => chegada.ordem < progresso);
  const duracaoDaVisita = Math.max(...passos.map((passo) => passo.inicio_ms + passo.duracao_ms));
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
            <Manchete chegaram={requisicoesQueChegaram} total={passos.length} falhas={terminou ? chegadas : falhasQueChegaram} />
          </p>
          <dl className="replay__contagem">
            <div>
              <dt>Arquivos</dt>
              <dd>
                {requisicoesQueChegaram}
                <span>/{passos.length}</span>
              </dd>
            </div>
            <div>
              <dt>Com falha</dt>
              <dd key={falhasQueChegaram.length} className={falhasQueChegaram.length > 0 ? "replay__contagem--alerta" : ""}>
                {falhasQueChegaram.length}
                <span>/{chegadas.length}</span>
              </dd>
            </div>
          </dl>
          <div className="replay__controles">
            <button
              type="button"
              className="replay__tocar"
              onClick={relogio.tocando ? relogio.pausar : relogio.tocar}
              aria-label={relogio.tocando ? "Pausar a visita" : "Tocar a visita"}
            >
              <Icone nome={relogio.tocando ? "pausar" : terminou ? "reiniciar" : "tocar"} tamanho={16} />
            </button>
            <input
              type="range"
              className="replay__linha-do-tempo"
              min={0}
              max={replay}
              step={10}
              value={relogio.tempo}
              onChange={(evento) => relogio.irPara(Number(evento.target.value))}
              aria-label="Momento da visita"
            />
            <span className="replay__total">{formatarDuracao(duracaoDaVisita / 1000)}</span>
          </div>
          <ul className="replay__legenda" aria-label="Legenda">
            <li>
              <span className="replay__simbolo replay__simbolo--requisicao" aria-hidden="true" />
              arquivo recebido
            </li>
            <li>
              <span className="replay__simbolo replay__simbolo--falha" aria-hidden="true" />
              trouxe biblioteca com falha
            </li>
            <li>
              <span className="replay__simbolo replay__simbolo--anel" aria-hidden="true" />
              anel: tipo de arquivo
            </li>
            <li>
              <span className="replay__simbolo replay__simbolo--giro" aria-hidden="true" />
              giro: ordem de chegada
            </li>
          </ul>
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
