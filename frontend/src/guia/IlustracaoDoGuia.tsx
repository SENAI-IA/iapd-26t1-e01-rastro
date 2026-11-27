import type { ReactNode } from "react";
import type { IlustracaoDoPasso } from "../conteudo/guia.ts";
import type { TerminalDoGuia } from "../conteudo/simulacoesDoGuia.ts";
import DesenhoDaRede from "./desenhos/passos/DesenhoDaRede.tsx";
import DesenhoDeEntrar from "./desenhos/passos/DesenhoDeEntrar.tsx";
import DesenhoDeExportar from "./desenhos/passos/DesenhoDeExportar.tsx";
import DesenhoDeNavegar from "./desenhos/passos/DesenhoDeNavegar.tsx";
import DesenhoDeNavegarEFechar from "./desenhos/passos/DesenhoDeNavegarEFechar.tsx";
import DesenhoDoCache from "./desenhos/passos/DesenhoDoCache.tsx";
import DesenhoDoRelatorio from "./desenhos/passos/DesenhoDoRelatorio.tsx";
import DesenhoDoRoboVisitando from "./desenhos/passos/DesenhoDoRoboVisitando.tsx";
import DesenhoDoSite from "./desenhos/passos/DesenhoDoSite.tsx";
import "./IlustracaoDoGuia.css";

export type DesenhoDoPasso = Exclude<IlustracaoDoPasso, TerminalDoGuia>;

const DESENHOS: Record<DesenhoDoPasso, ReactNode> = {
  site: <DesenhoDoSite />,
  rede: <DesenhoDaRede />,
  cache: <DesenhoDoCache />,
  navegar: <DesenhoDeNavegar />,
  exportar: <DesenhoDeExportar />,
  entrar: <DesenhoDeEntrar />,
  "robo-visita": <DesenhoDoRoboVisitando />,
  "navegar-e-fechar": <DesenhoDeNavegarEFechar />,
  relatorio: <DesenhoDoRelatorio />,
};

interface Props {
  ilustracao: DesenhoDoPasso;
}

export default function IlustracaoDoGuia({ ilustracao }: Props) {
  return (
    <svg className="ilustracao-do-guia" viewBox="0 0 320 190" aria-hidden="true">
      {DESENHOS[ilustracao]}
    </svg>
  );
}
