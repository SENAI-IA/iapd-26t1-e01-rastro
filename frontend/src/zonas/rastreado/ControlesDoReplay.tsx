import Icone, { type NomeDoIcone } from "../../basicos/Icone.tsx";
import type { RelogioDoReplay } from "../../hooks/usarRelogioDoReplay.ts";
import { formatarDuracao } from "../../formatacao/formato.ts";

interface Props {
  relogio: RelogioDoReplay;
  duracaoDoReplay: number;
  duracaoDaVisita: number;
}

function iconeDoBotao(tocando: boolean, terminou: boolean): NomeDoIcone {
  if (tocando) {
    return "pausar";
  }
  return terminou ? "reiniciar" : "tocar";
}

export default function ControlesDoReplay({ relogio, duracaoDoReplay, duracaoDaVisita }: Props) {
  const terminou = relogio.tempo >= duracaoDoReplay;
  return (
    <div className="replay__controles">
      <button
        type="button"
        className="replay__tocar"
        onClick={relogio.tocando ? relogio.pausar : relogio.tocar}
        aria-label={relogio.tocando ? "Pausar a visita" : "Tocar a visita"}
      >
        <Icone nome={iconeDoBotao(relogio.tocando, terminou)} tamanho={16} />
      </button>
      <input
        type="range"
        className="replay__linha-do-tempo"
        min={0}
        max={duracaoDoReplay}
        step={10}
        value={relogio.tempo}
        onChange={(evento) => relogio.irPara(Number(evento.target.value))}
        aria-label="Momento da visita"
      />
      <span className="replay__total">{formatarDuracao(duracaoDaVisita / 1000)}</span>
    </div>
  );
}
