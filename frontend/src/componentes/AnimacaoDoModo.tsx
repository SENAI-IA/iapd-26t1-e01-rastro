import type { ReactNode } from "react";
import type { ModoDeUso } from "../dados/guia.ts";
import "./AnimacaoDoModo.css";

const POSICOES = [2, 98, 194];

function Robo() {
  return (
    <>
      <line className="modo-anim__traco modo-anim__traco--destaque" x1="0" y1="-5" x2="0" y2="-8" />
      <circle className="modo-anim__ponto" cx="0" cy="-9" r="1.4" />
      <rect className="modo-anim__traco modo-anim__traco--destaque modo-anim__cabeca" x="-6" y="-5" width="12" height="10" rx="2" />
      <circle className="modo-anim__ponto" cx="-2.5" cy="0" r="1.2" />
      <circle className="modo-anim__ponto" cx="2.5" cy="0" r="1.2" />
    </>
  );
}

function Cursor() {
  return <path className="modo-anim__traco modo-anim__traco--destaque modo-anim__seta" d="M0 0 l0 12 l3.4 -3.4 l2.6 5.2 l2 -1 l-2.6 -5.2 l4.8 0 z" />;
}

function Janela({ children }: { children: ReactNode }) {
  return (
    <>
      <line className="modo-anim__traco" x1="0" y1="11" x2="68" y2="11" />
      <circle className="modo-anim__traco" cx="7" cy="6" r="1.6" />
      <circle className="modo-anim__traco" cx="13" cy="6" r="1.6" />
      {children}
    </>
  );
}

function Links() {
  return (
    <>
      <rect className="modo-anim__traco" x="8" y="18" width="16" height="7" rx="1.5" />
      <rect className="modo-anim__traco" x="27" y="18" width="16" height="7" rx="1.5" />
      <rect className="modo-anim__traco" x="46" y="18" width="16" height="7" rx="1.5" />
      <line className="modo-anim__traco modo-anim__traco--suave" x1="8" y1="34" x2="60" y2="34" />
      <line className="modo-anim__traco modo-anim__traco--suave" x1="8" y1="42" x2="48" y2="42" />
    </>
  );
}

function Terminal({ comando }: { comando: string }) {
  return (
    <>
      <line className="modo-anim__traco" x1="0" y1="11" x2="68" y2="11" />
      <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--forte" x="6" y="25">
        $ rastro
      </text>
      <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--forte" x="6" y="35">
        gravar
      </text>
      {comando && (
        <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--destaque modo-anim__texto--forte" x="6" y="45">
          {comando}
        </text>
      )}
      <rect className="modo-anim__cursor-texto" x={comando ? 40 : 6} y={comando ? 39 : 39} width="4" height="7" />
    </>
  );
}

function Relatorio() {
  return (
    <Janela>
      <rect className="modo-anim__traco modo-anim__traco--destaque" x="8" y="17" width="16" height="10" rx="1.5" />
      <rect className="modo-anim__traco" x="27" y="17" width="16" height="10" rx="1.5" />
      <rect className="modo-anim__traco" x="46" y="17" width="16" height="10" rx="1.5" />
      <circle className="modo-anim__traco" cx="20" cy="41" r="8" />
      <line className="modo-anim__traco modo-anim__traco--destaque modo-anim__traco--grosso" x1="36" y1="36" x2="60" y2="36" />
      <line className="modo-anim__traco modo-anim__traco--destaque modo-anim__traco--grosso" x1="36" y1="44" x2="52" y2="44" />
    </Janela>
  );
}

const QUADROS: Record<ModoDeUso, { desenhos: ReactNode[]; legendas: string[] }> = {
  devtools: {
    legendas: ["Abre o F12", "Exporta", "Relatório"],
    desenhos: [
      <Janela key="1">
        <line className="modo-anim__traco" x1="0" y1="30" x2="68" y2="30" />
        <line className="modo-anim__linha" pathLength="1" x1="6" y1="38" x2="56" y2="38" />
        <line className="modo-anim__linha modo-anim__linha--2" pathLength="1" x1="6" y1="45" x2="44" y2="45" />
        <g className="modo-anim__tecla">
          <rect className="modo-anim__traco modo-anim__traco--destaque" x="22" y="14" width="24" height="12" rx="2" />
          <text className="modo-anim__texto modo-anim__texto--destaque modo-anim__texto--forte" x="27" y="23">
            F12
          </text>
        </g>
      </Janela>,
      <g key="2">
        <g className="modo-anim__pulo">
          <path className="modo-anim__traco modo-anim__traco--destaque" d="M24 10 h14 l8 8 v26 h-22 z M38 10 v8 h8" />
        </g>
        <text className="modo-anim__texto modo-anim__texto--forte" x="22" y="54">
          site.har
        </text>
      </g>,
      <Relatorio key="3" />,
    ],
  },
  gravar: {
    legendas: ["Você roda", "Navega e fecha", "Relatório"],
    desenhos: [
      <Terminal key="1" comando="" />,
      <Janela key="2">
        <Links />
        <g transform="translate(14 21)">
          <g className="modo-anim__passeio">
            <Cursor />
          </g>
        </g>
        <g className="modo-anim__fechar">
          <path className="modo-anim__traco modo-anim__traco--destaque" d="M58 3.5 l5 5 M63 3.5 l-5 5" />
        </g>
      </Janela>,
      <Relatorio key="3" />,
    ],
  },
  robo: {
    legendas: ["Você roda", "O robô navega", "Relatório"],
    desenhos: [
      <Terminal key="1" comando="--robo" />,
      <Janela key="2">
        <Links />
        <g transform="translate(16 22)">
          <g className="modo-anim__robo">
            <Robo />
          </g>
        </g>
        <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--destaque modo-anim__contador modo-anim__contador--1" x="46" y="52">
          1/20
        </text>
        <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--destaque modo-anim__contador modo-anim__contador--2" x="46" y="52">
          2/20
        </text>
        <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--destaque modo-anim__contador modo-anim__contador--3" x="46" y="52">
          3/20
        </text>
      </Janela>,
      <Relatorio key="3" />,
    ],
  },
};

interface Props {
  modo: ModoDeUso;
}

export default function AnimacaoDoModo({ modo }: Props) {
  const { desenhos, legendas } = QUADROS[modo];
  return (
    <svg className="modo-anim" viewBox="0 0 264 76" aria-hidden="true">
      {desenhos.map((desenho, indice) => (
        <g key={legendas[indice]} transform={`translate(${POSICOES[indice]} 2)`}>
          <rect
            className={`modo-anim__traco modo-anim__quadro modo-anim__quadro--${indice + 1}`}
            x="0"
            y="0"
            width="68"
            height="56"
            rx="3"
          />
          {desenho}
          <text className="modo-anim__legenda" x="34" y="70" textAnchor="middle">
            {legendas[indice]}
          </text>
        </g>
      ))}
      <path className="modo-anim__traco modo-anim__traco--suave-seta" d="M76 30 h14 M86 26 l4 4 l-4 4" />
      <path className="modo-anim__traco modo-anim__traco--suave-seta" d="M172 30 h14 M182 26 l4 4 l-4 4" />
    </svg>
  );
}
