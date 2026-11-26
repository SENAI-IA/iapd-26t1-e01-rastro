import LinhasQueAparecem from "../pecas/LinhasQueAparecem.tsx";

export default function DesenhoDoCache() {
  return (
    <>
      <rect className="ilustracao-do-guia__traco" x="8" y="30" width="304" height="130" rx="4" />
      <line className="ilustracao-do-guia__traco" x1="8" y1="66" x2="312" y2="66" />
      <circle className="ilustracao-do-guia__traco" cx="30" cy="48" r="7" />
      <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" x="50" y="41" width="14" height="14" rx="2" />
      <path className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" d="M53 48 l3.5 3.5 l6 -7" />
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--forte" x="72" y="52">
        Desativar cache
      </text>
      <g className="ilustracao-do-guia__giro">
        <path className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" d="M268 40 a9 9 0 1 0 8 6" />
        <path className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" d="M272 38 l4 3 l-1 5" />
      </g>
      <rect className="ilustracao-do-guia__realce" x="18" y="73" width="44" height="18" rx="3" />
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--destaque ilustracao-do-guia__texto--forte" x="27" y="86">
        Todos
      </text>
      <text className="ilustracao-do-guia__texto" x="74" y="86">
        Fetch/XHR
      </text>
      <text className="ilustracao-do-guia__texto" x="138" y="86">
        JS
      </text>
      <text className="ilustracao-do-guia__texto" x="162" y="86">
        CSS
      </text>
      <LinhasQueAparecem primeiraLinha={106} comprimentos={[250, 200, 230, 170]} />
      <rect className="ilustracao-do-guia__traco" x="196" y="168" width="104" height="16" rx="3" />
      <text className="ilustracao-do-guia__texto" x="226" y="179.5">
        Ctrl + R
      </text>
    </>
  );
}
