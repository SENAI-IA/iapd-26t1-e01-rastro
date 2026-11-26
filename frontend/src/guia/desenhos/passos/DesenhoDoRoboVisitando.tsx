import Janela from "../pecas/Janela.tsx";
import MenuDeLinks from "../pecas/MenuDeLinks.tsx";
import Robo from "../pecas/Robo.tsx";

export default function DesenhoDoRoboVisitando() {
  return (
    <Janela tamanho="grande">
      <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" x="62" y="14" width="200" height="14" rx="7" />
      <text className="ilustracao-do-guia__texto" x="76" y="24.5">
        site.com.br
      </text>
      <MenuDeLinks tamanho="grande" />
      <rect className="ilustracao-do-guia__traco" x="24" y="72" width="128" height="34" rx="3" />
      <rect className="ilustracao-do-guia__traco" x="160" y="72" width="136" height="34" rx="3" />
      <Robo x={54} y={54} tamanho="grande" />
      <line className="ilustracao-do-guia__traco" x1="8" y1="116" x2="312" y2="116" />
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--mono ilustracao-do-guia__digita ilustracao-do-guia__digita--2" x="22" y="134">
        [1/20] /
      </text>
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--mono ilustracao-do-guia__digita ilustracao-do-guia__digita--3" x="22" y="150">
        [2/20] /produtos
      </text>
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--mono ilustracao-do-guia__digita ilustracao-do-guia__digita--4" x="22" y="166">
        [3/20] /contato
      </text>
      <text
        className="ilustracao-do-guia__texto ilustracao-do-guia__texto--mono ilustracao-do-guia__texto--destaque ilustracao-do-guia__texto--forte ilustracao-do-guia__digita ilustracao-do-guia__digita--5"
        x="170"
        y="166"
      >
        Parou: fim dos links
      </text>
    </Janela>
  );
}
