import type { PassoDaVisita } from "../../relatorio/tiposDoRelatorio.ts";
import type { Chegada } from "../../calculosDeTela/chegadasDaVisita.ts";
import { estadoDoRadar, type EstadoDoRadar } from "../../calculosDeTela/estadoDoRadar.ts";
import { CENTRO, enquadramento, fatiaDoRastro } from "../../calculosDeTela/geometriaDoRadar.ts";
import { caminhoDaUrl } from "../../formatacao/formato.ts";
import AneisDoRadar from "./AneisDoRadar.tsx";
import CentroDoRadar from "./CentroDoRadar.tsx";
import FundoDoRadar from "./FundoDoRadar.tsx";
import RotuloDaFalha from "./RotuloDaFalha.tsx";
import "./RadarDaVisita.css";

const ABERTURA_DO_RASTRO = 40;

interface Props {
  passos: PassoDaVisita[];
  chegadas: Chegada[];
  progresso: number;
  bibliotecaEmDestaque: string | null;
  aoEscolherBiblioteca: (id: string) => void;
  aoDestacarBiblioteca: (id: string | null) => void;
}

function classeDoRadar(estado: EstadoDoRadar): string {
  const classes = ["radar"];
  if (estado.emAlerta) {
    classes.push("radar--alerta");
  }
  if (estado.terminou) {
    classes.push("radar--fim");
  }
  if (estado.temFalha) {
    classes.push("radar--com-falha");
  }
  return classes.join(" ");
}

export default function RadarDaVisita({
  passos,
  chegadas,
  progresso,
  bibliotecaEmDestaque,
  aoEscolherBiblioteca,
  aoDestacarBiblioteca,
}: Props) {
  const estado = estadoDoRadar(passos, chegadas, progresso);
  return (
    <svg
      className={classeDoRadar(estado)}
      viewBox={enquadramento(estado.ladosComRotulo)}
      role="img"
      aria-label="Radar da visita: cada ponto é uma requisição do HAR, na ordem em que chegou; os nomes marcam as bibliotecas com falha"
    >
      <FundoDoRadar />
      <AneisDoRadar passos={passos} camadasComFalha={estado.camadasComFalha} />
      {!estado.terminou && (
        <>
          <path className="radar__rastro" d={fatiaDoRastro(estado.anguloAtual, ABERTURA_DO_RASTRO)} />
          <line className="radar__ponteiro" x1={CENTRO.x} y1={CENTRO.y} x2={estado.ponteiro.x} y2={estado.ponteiro.y} />
        </>
      )}
      {estado.recentes.map(({ ordem, ponto }) => (
        <line key={`r${ordem}`} className="radar__recente" x1={CENTRO.x} y1={CENTRO.y} x2={ponto.x} y2={ponto.y} />
      ))}
      {estado.chegaram.map(({ ordem, ponto }) => (
        <circle key={ordem} className="radar__requisicao" cx={ponto.x} cy={ponto.y} r={2.8}>
          <title>{caminhoDaUrl(passos[ordem].url)}</title>
        </circle>
      ))}
      {estado.rotulos.map((rotulo) => (
        <RotuloDaFalha
          key={rotulo.item.id}
          rotulo={rotulo}
          emDestaque={bibliotecaEmDestaque === rotulo.item.id}
          aoEscolher={aoEscolherBiblioteca}
          aoDestacar={aoDestacarBiblioteca}
        />
      ))}
      {estado.falhasRepetidas.map(({ ordem, ponto }) => (
        <circle key={`f${ordem}`} className="radar__alvo radar__alvo--repetido" cx={ponto.x} cy={ponto.y} r={4.5} />
      ))}
      <CentroDoRadar momento={estado.momento} />
    </svg>
  );
}
