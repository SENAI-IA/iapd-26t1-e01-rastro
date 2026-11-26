import Cursor from "../pecas/Cursor.tsx";

export default function NavegadorDeLogin() {
  return (
    <>
      <rect className="ilustracao-do-guia__traco" x="8" y="18" width="172" height="154" rx="4" />
      <line className="ilustracao-do-guia__traco" x1="8" y1="42" x2="180" y2="42" />
      <circle className="ilustracao-do-guia__traco" cx="22" cy="30" r="4" />
      <circle className="ilustracao-do-guia__traco" cx="34" cy="30" r="4" />
      <text className="ilustracao-do-guia__texto" x="50" y="33.5">
        Navegador
      </text>
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--forte" x="24" y="64">
        Entrar no site
      </text>
      <rect className="ilustracao-do-guia__traco" x="24" y="74" width="140" height="20" rx="3" />
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__digita ilustracao-do-guia__digita--1" x="32" y="88">
        maria@empresa.com
      </text>
      <rect className="ilustracao-do-guia__traco" x="24" y="102" width="140" height="20" rx="3" />
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__digita ilustracao-do-guia__digita--2" x="32" y="117">
        ••••••••
      </text>
      <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" x="24" y="134" width="64" height="22" rx="3" />
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--destaque ilustracao-do-guia__texto--forte" x="40" y="148.5">
        Entrar
      </text>
      <Cursor x={82} y={150} tamanho="medio" animacao="ilustracao-do-guia__digita ilustracao-do-guia__digita--3" />
    </>
  );
}
