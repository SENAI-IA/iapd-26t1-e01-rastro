import type { ReactNode } from "react";
import type { ModoDeUso } from "../conteudo/guia.ts";
import MiniaturaDeNavegarEFechar from "./desenhos/modos/MiniaturaDeNavegarEFechar.tsx";
import MiniaturaDoF12 from "./desenhos/modos/MiniaturaDoF12.tsx";
import MiniaturaDoHar from "./desenhos/modos/MiniaturaDoHar.tsx";
import MiniaturaDoRelatorio from "./desenhos/modos/MiniaturaDoRelatorio.tsx";
import MiniaturaDoRoboNavegando from "./desenhos/modos/MiniaturaDoRoboNavegando.tsx";
import MiniaturaDoTerminal from "./desenhos/modos/MiniaturaDoTerminal.tsx";
import QuadroDoModo from "./QuadroDoModo.tsx";
import "./AnimacaoDoModo.css";

const POSICOES = [2, 98, 194];

const QUADROS: Record<ModoDeUso, { desenhos: ReactNode[]; legendas: string[] }> = {
  devtools: {
    legendas: ["Abre o F12", "Exporta", "Relatório"],
    desenhos: [<MiniaturaDoF12 key="1" />, <MiniaturaDoHar key="2" />, <MiniaturaDoRelatorio key="3" />],
  },
  gravar: {
    legendas: ["Você roda", "Navega e fecha", "Relatório"],
    desenhos: [<MiniaturaDoTerminal comando="" key="1" />, <MiniaturaDeNavegarEFechar key="2" />, <MiniaturaDoRelatorio key="3" />],
  },
  robo: {
    legendas: ["Você roda", "O robô navega", "Relatório"],
    desenhos: [<MiniaturaDoTerminal comando="--robo" key="1" />, <MiniaturaDoRoboNavegando key="2" />, <MiniaturaDoRelatorio key="3" />],
  },
};

interface Props {
  modo: ModoDeUso;
}

export default function AnimacaoDoModo({ modo }: Props) {
  const { desenhos, legendas } = QUADROS[modo];
  return (
    <svg className="animacao-do-modo" viewBox="0 0 264 76" aria-hidden="true">
      {desenhos.map((desenho, indice) => (
        <QuadroDoModo key={legendas[indice]} posicao={POSICOES[indice]} numero={indice + 1} legenda={legendas[indice]}>
          {desenho}
        </QuadroDoModo>
      ))}
      <path className="animacao-do-modo__traco animacao-do-modo__traco--suave-seta" d="M76 30 h14 M86 26 l4 4 l-4 4" />
      <path className="animacao-do-modo__traco animacao-do-modo__traco--suave-seta" d="M172 30 h14 M182 26 l4 4 l-4 4" />
    </svg>
  );
}
