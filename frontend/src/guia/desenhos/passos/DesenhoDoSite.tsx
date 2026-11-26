import Cursor from "../pecas/Cursor.tsx";
import Janela from "../pecas/Janela.tsx";

export default function DesenhoDoSite() {
  return (
    <Janela tamanho="grande">
      <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" x="62" y="14" width="200" height="14" rx="7" />
      <text className="ilustracao-do-guia__texto" x="76" y="24.5">
        loja.homologacao.local
      </text>
      <rect className="ilustracao-do-guia__traco" x="24" y="48" width="272" height="52" rx="3" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="116" x2="210" y2="116" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="130" x2="160" y2="130" />
      <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" x="24" y="148" width="76" height="22" rx="3" />
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--destaque" x="44" y="162.5">
        Entrar
      </text>
      <Cursor x={150} y={150} tamanho="grande" animacao="ilustracao-do-guia__cursor" />
    </Janela>
  );
}
