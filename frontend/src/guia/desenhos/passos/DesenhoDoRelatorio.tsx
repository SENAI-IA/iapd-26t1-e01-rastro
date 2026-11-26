import Janela from "../pecas/Janela.tsx";

export default function DesenhoDoRelatorio() {
  return (
    <Janela tamanho="grande">
      <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque ilustracao-do-guia__pulsa" x="22" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao-do-guia__traco" x="92" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao-do-guia__traco" x="162" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao-do-guia__traco" x="232" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao-do-guia__traco" x="22" y="90" width="166" height="80" rx="3" />
      <circle className="ilustracao-do-guia__traco" cx="105" cy="130" r="32" />
      <circle className="ilustracao-do-guia__traco" cx="105" cy="130" r="20" />
      <circle className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" cx="128" cy="112" r="4" />
      <circle className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" cx="90" cy="146" r="4" />
      <rect className="ilustracao-do-guia__traco" x="196" y="90" width="100" height="80" rx="3" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque ilustracao-do-guia__traco--grosso" x1="206" y1="106" x2="284" y2="106" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque ilustracao-do-guia__traco--grosso" x1="206" y1="122" x2="252" y2="122" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque ilustracao-do-guia__traco--grosso" x1="206" y1="138" x2="232" y2="138" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque ilustracao-do-guia__traco--grosso" x1="206" y1="154" x2="214" y2="154" />
    </Janela>
  );
}
