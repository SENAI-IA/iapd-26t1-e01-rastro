import Cursor from "../pecas/Cursor.tsx";
import Janela from "../pecas/Janela.tsx";
import MenuDeLinks from "../pecas/MenuDeLinks.tsx";

export default function DesenhoDeNavegarEFechar() {
  return (
    <Janela tamanho="grande">
      <g className="ilustracao-do-guia__pulsa-fechar">
        <circle className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" cx="296" cy="21" r="7" />
        <path className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" d="M292.5 17.5 l7 7 M299.5 17.5 l-7 7" />
      </g>
      <MenuDeLinks tamanho="grande" />
      <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x="24" y="76" width="272" height="30" rx="3" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="128" x2="250" y2="128" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="144" x2="210" y2="144" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="160" x2="230" y2="160" />
      <Cursor x={60} y={52} tamanho="medio" animacao="ilustracao-do-guia__cabeca ilustracao-do-guia__vai-fechar" />
    </Janela>
  );
}
