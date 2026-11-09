import type { KeyboardEvent } from "react";
import type { Camada, PassoDaVisita, Prioridade } from "../tipos.ts";
import type { Chegada } from "./chegadasDaVisita.ts";
import { formatarDuracao } from "./formato.ts";
import {
  anguloDaOrdem,
  caminhoDoFio,
  CENTRO,
  enquadramento,
  fatiaDoRastro,
  ladoDoPonto,
  pontoNoCirculo,
  posicionarRotulos,
  RAIO_DA_CAMADA,
  RAIO_EXTERNO,
  raioComEspalhamento,
} from "./geometriaDoRadar.ts";
import "./RadarDaVisita.css";

const NOME_DA_CAMADA: Record<Camada, string> = {
  pagina: "páginas HTML",
  script: "scripts JS",
  estilo: "estilos CSS",
  dados: "dados e APIs",
  midia: "imagens e fontes",
};
const CAMADAS = Object.keys(RAIO_DA_CAMADA) as Camada[];
const TOM_DA_PRIORIDADE: Record<Prioridade, string> = {
  alta: "critico",
  media: "serio",
  baixa: "neutro",
  "a avaliar": "neutro",
};
const RASTRO_RECENTE = 4;
const ALERTA_DEPOIS_DA_FALHA = 6;

interface Props {
  passos: PassoDaVisita[];
  chegadas: Chegada[];
  progresso: number;
  bibliotecaEmDestaque: string | null;
  aoEscolherBiblioteca: (id: string) => void;
  aoDestacarBiblioteca: (id: string | null) => void;
}

function caminhoDaUrl(url: string): string {
  try {
    return new URL(url).pathname;
  } catch {
    return url;
  }
}

function acionarComTeclado(acao: () => void) {
  return (evento: KeyboardEvent) => {
    if (evento.key === "Enter" || evento.key === " ") {
      evento.preventDefault();
      acao();
    }
  };
}

export default function RadarDaVisita({
  passos,
  chegadas,
  progresso,
  bibliotecaEmDestaque,
  aoEscolherBiblioteca,
  aoDestacarBiblioteca,
}: Props) {
  const total = passos.length;
  const pontoDaOrdem = (ordem: number) =>
    pontoNoCirculo(raioComEspalhamento(passos[ordem].camada, passos[ordem].indice_requisicao), anguloDaOrdem(ordem, total));
  const chegaram = passos.map((_, ordem) => ordem).filter((ordem) => ordem < progresso);
  const comFalha = chegaram.filter((ordem) => passos[ordem].prioridade !== null);
  const terminou = progresso >= total;
  const recentes = terminou ? [] : chegaram.filter((ordem) => progresso - ordem < RASTRO_RECENTE);
  const ultimaFalha = comFalha.at(-1);
  const emAlerta = ultimaFalha !== undefined && progresso - ultimaFalha < ALERTA_DEPOIS_DA_FALHA;
    const camadasComFalha = new Set(comFalha.map((ordem) => passos[ordem].camada));
  const anguloAtual = anguloDaOrdem(Math.min(progresso, total), total);
  const ponteiro = pontoNoCirculo(RAIO_EXTERNO, anguloAtual);
  const momento = chegaram.length > 0 ? passos[chegaram.length - 1].inicio_ms : 0;
  const rotulos = posicionarRotulos(
    chegadas
      .filter((chegada) => chegada.ordem < progresso)
      .map((chegada) => ({ item: chegada, ancora: pontoDaOrdem(chegada.ordem) })),
  );

  const ladosComRotulo = new Set(chegadas.map((chegada) => ladoDoPonto(pontoDaOrdem(chegada.ordem))));
  const classes = ["radar", emAlerta ? "radar--alerta" : "", terminou ? "radar--fim" : "", comFalha.length > 0 ? "radar--com-falha" : ""];

  return (
    <svg
      className={classes.join(" ")}
      viewBox={enquadramento(ladosComRotulo)}
      role="img"
      aria-label="Radar da visita: cada ponto é uma requisição do HAR, na ordem em que chegou; os nomes marcam as bibliotecas com falha"
    >
      <defs>
        <radialGradient id="radar-fundo">
          <stop offset="0" className="radar__fundo-centro" />
          <stop offset="1" className="radar__fundo-borda" />
        </radialGradient>
      </defs>
      <circle className="radar__disco" cx={CENTRO.x} cy={CENTRO.y} r={RAIO_EXTERNO} fill="url(#radar-fundo)" />

      {CAMADAS.map((camada) => (
        <g key={camada} className={camadasComFalha.has(camada) ? "radar__camada radar__camada--com-falha" : "radar__camada"}>
          <circle className="radar__anel" cx={CENTRO.x} cy={CENTRO.y} r={RAIO_DA_CAMADA[camada]} />
          <text className="radar__nome-da-camada" x={CENTRO.x} y={CENTRO.y - RAIO_DA_CAMADA[camada] + 3.5}>
            {NOME_DA_CAMADA[camada]} · {passos.filter((passo) => passo.camada === camada).length}
          </text>
        </g>
      ))}

      {!terminou && (
        <>
          <path className="radar__rastro" d={fatiaDoRastro(anguloAtual, 40)} />
          <line className="radar__ponteiro" x1={CENTRO.x} y1={CENTRO.y} x2={ponteiro.x} y2={ponteiro.y} />
        </>
      )}

      {recentes.map((ordem) => {
        const ponto = pontoDaOrdem(ordem);
        return <line key={`r${ordem}`} className="radar__recente" x1={CENTRO.x} y1={CENTRO.y} x2={ponto.x} y2={ponto.y} />;
      })}

      {chegaram.map((ordem) => {
        const ponto = pontoDaOrdem(ordem);
        return (
          <circle key={ordem} className="radar__requisicao" cx={ponto.x} cy={ponto.y} r={2.8}>
            <title>{caminhoDaUrl(passos[ordem].url)}</title>
          </circle>
        );
      })}

      {rotulos.map(({ item: chegada, ancora, lado, x, y }) => {
        const tom = TOM_DA_PRIORIDADE[chegada.prioridade];
        const emDestaque = bibliotecaEmDestaque === chegada.id;
        const escolher = () => aoEscolherBiblioteca(chegada.id);
        return (
          <g
            key={chegada.id}
            className={`radar__falha radar__falha--${tom}${emDestaque ? " radar__falha--destaque" : ""}`}
            role="button"
            tabIndex={0}
            aria-label={`${chegada.pacote} ${chegada.versao}, prioridade ${chegada.prioridade}: ver nos detalhes`}
            onClick={escolher}
            onKeyDown={acionarComTeclado(escolher)}
            onMouseEnter={() => aoDestacarBiblioteca(chegada.id)}
            onMouseLeave={() => aoDestacarBiblioteca(null)}
            onFocus={() => aoDestacarBiblioteca(chegada.id)}
            onBlur={() => aoDestacarBiblioteca(null)}
          >
            <line className="radar__fio-do-centro" x1={CENTRO.x} y1={CENTRO.y} x2={ancora.x} y2={ancora.y} />
            <path className="radar__fio-do-rotulo" d={caminhoDoFio(ancora, { x, y, lado })} />
            <circle className="radar__onda" cx={ancora.x} cy={ancora.y} r={8} />
            <circle className="radar__pulso" cx={ancora.x} cy={ancora.y} r={7} />
            <circle className="radar__alvo" cx={ancora.x} cy={ancora.y} r={7} />
            <text className="radar__rotulo" x={x} y={y + 4} textAnchor={lado === "direita" ? "start" : "end"}>
              <tspan className="radar__pacote">{chegada.pacote}</tspan>
              <tspan className="radar__versao"> {chegada.versao}</tspan>
            </text>
          </g>
        );
      })}

      {comFalha
        .filter((ordem) => !chegadas.some((chegada) => chegada.ordem === ordem))
        .map((ordem) => {
          const ponto = pontoDaOrdem(ordem);
          return <circle key={`f${ordem}`} className="radar__alvo radar__alvo--repetido" cx={ponto.x} cy={ponto.y} r={4.5} />;
        })}

      <circle className="radar__centro" cx={CENTRO.x} cy={CENTRO.y} r={34} />
      <text className="radar__tempo" x={CENTRO.x} y={CENTRO.y + 3}>
        {formatarDuracao(momento / 1000)}
      </text>
      <text className="radar__legenda-tempo" x={CENTRO.x} y={CENTRO.y + 17}>
        de visita
      </text>
    </svg>
  );
}
