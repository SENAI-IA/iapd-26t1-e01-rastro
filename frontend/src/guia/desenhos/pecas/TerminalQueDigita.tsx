import {
  CURSOR_ABAIXO_DA_ULTIMA_LINHA,
  posicionarLinhas,
  type DestaqueDaLinha,
  type LinhaDoTerminal,
  type LinhaPosicionada,
} from "../../../calculosDeTela/linhasDoTerminal.ts";
import MolduraDeTerminal from "./MolduraDeTerminal.tsx";

const CLASSES_DO_DESTAQUE: Record<DestaqueDaLinha, string[]> = {
  comando: ["ilustracao__texto--forte"],
  continuacao: ["ilustracao__texto--forte"],
  saida: [],
  resultado: ["ilustracao__texto--destaque", "ilustracao__texto--forte"],
};

function classeDaLinha(linha: LinhaPosicionada): string {
  return [
    "ilustracao__texto",
    "ilustracao__texto--mono",
    ...CLASSES_DO_DESTAQUE[linha.destaque],
    "ilustracao__digita",
    `ilustracao__digita--${linha.ordemDeAparecer}`,
  ].join(" ");
}

interface Props {
  linhas: LinhaDoTerminal[];
}

export default function TerminalQueDigita({ linhas }: Props) {
  const posicionadas = posicionarLinhas(linhas);
  const ultimaLinha = posicionadas[posicionadas.length - 1].y;
  return (
    <MolduraDeTerminal>
      {posicionadas.map((linha) => (
        <text key={linha.texto} className={classeDaLinha(linha)} x="22" y={linha.y}>
          {linha.texto}
        </text>
      ))}
      <rect className="ilustracao__cursor-texto" x="22" y={ultimaLinha + CURSOR_ABAIXO_DA_ULTIMA_LINHA} width="7" height="12" />
    </MolduraDeTerminal>
  );
}
