import type { KeyboardEvent } from "react";
import type { Prioridade } from "../../relatorio/tiposDoRelatorio.ts";
import type { ChegadaDeBiblioteca } from "../../calculosDeTela/chegadasDaVisita.ts";
import { caminhoDoFio, CENTRO, type Rotulo } from "../../calculosDeTela/geometriaDoRadar.ts";

const TOM_DA_PRIORIDADE: Record<Prioridade, string> = {
  alta: "critico",
  media: "serio",
  baixa: "neutro",
  "a avaliar": "neutro",
};

function acionarComTeclado(acao: () => void) {
  return (evento: KeyboardEvent) => {
    const teclaQueAciona = evento.key === "Enter" || evento.key === " ";
    if (!teclaQueAciona) {
      return;
    }
    evento.preventDefault();
    acao();
  };
}

interface Props {
  rotulo: Rotulo<ChegadaDeBiblioteca>;
  emDestaque: boolean;
  aoEscolher: (id: string) => void;
  aoDestacar: (id: string | null) => void;
}

export default function RotuloDaFalha({ rotulo, emDestaque, aoEscolher, aoDestacar }: Props) {
  const { item: chegada, ancora, lado, x, y } = rotulo;
  const escolher = () => aoEscolher(chegada.id);
  return (
    <g
      className={`radar__falha radar__falha--${TOM_DA_PRIORIDADE[chegada.prioridade]}${emDestaque ? " radar__falha--destaque" : ""}`}
      role="button"
      tabIndex={0}
      aria-label={`${chegada.pacote} ${chegada.versao}, prioridade ${chegada.prioridade}: ver nos detalhes`}
      onClick={escolher}
      onKeyDown={acionarComTeclado(escolher)}
      onMouseEnter={() => aoDestacar(chegada.id)}
      onMouseLeave={() => aoDestacar(null)}
      onFocus={() => aoDestacar(chegada.id)}
      onBlur={() => aoDestacar(null)}
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
}
