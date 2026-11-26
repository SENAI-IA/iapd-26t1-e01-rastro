import type { ReactNode } from "react";
import type { IlustracaoDoPasso } from "../conteudo/guia.ts";
import { LINHAS_DO_TERMINAL } from "../conteudo/terminaisDoGuia.ts";
import DesenhoDaRede from "./desenhos/passos/DesenhoDaRede.tsx";
import DesenhoDeEntrar from "./desenhos/passos/DesenhoDeEntrar.tsx";
import DesenhoDeExportar from "./desenhos/passos/DesenhoDeExportar.tsx";
import DesenhoDeNavegar from "./desenhos/passos/DesenhoDeNavegar.tsx";
import DesenhoDeNavegarEFechar from "./desenhos/passos/DesenhoDeNavegarEFechar.tsx";
import DesenhoDoCache from "./desenhos/passos/DesenhoDoCache.tsx";
import DesenhoDoRelatorio from "./desenhos/passos/DesenhoDoRelatorio.tsx";
import DesenhoDoRoboVisitando from "./desenhos/passos/DesenhoDoRoboVisitando.tsx";
import DesenhoDoSite from "./desenhos/passos/DesenhoDoSite.tsx";
import TerminalQueDigita from "./desenhos/pecas/TerminalQueDigita.tsx";
import "./IlustracaoDoGuia.css";

const DESENHOS: Record<IlustracaoDoPasso, ReactNode> = {
  site: <DesenhoDoSite />,
  rede: <DesenhoDaRede />,
  cache: <DesenhoDoCache />,
  navegar: <DesenhoDeNavegar />,
  exportar: <DesenhoDeExportar />,
  instalar: <TerminalQueDigita linhas={LINHAS_DO_TERMINAL.instalar} />,
  playwright: <TerminalQueDigita linhas={LINHAS_DO_TERMINAL.playwright} />,
  gravar: <TerminalQueDigita linhas={LINHAS_DO_TERMINAL.gravar} />,
  robo: <TerminalQueDigita linhas={LINHAS_DO_TERMINAL.robo} />,
  terminal: <TerminalQueDigita linhas={LINHAS_DO_TERMINAL.terminal} />,
  entrar: <DesenhoDeEntrar />,
  "robo-visita": <DesenhoDoRoboVisitando />,
  "navegar-e-fechar": <DesenhoDeNavegarEFechar />,
  pentest: <TerminalQueDigita linhas={LINHAS_DO_TERMINAL.pentest} />,
  relatorio: <DesenhoDoRelatorio />,
};

interface Props {
  ilustracao: IlustracaoDoPasso;
}

export default function IlustracaoDoGuia({ ilustracao }: Props) {
  return (
    <svg className="ilustracao-do-guia" viewBox="0 0 320 190" aria-hidden="true">
      {DESENHOS[ilustracao]}
    </svg>
  );
}
