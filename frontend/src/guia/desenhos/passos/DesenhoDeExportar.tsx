export default function DesenhoDeExportar() {
  return (
    <>
      <rect className="ilustracao__traco" x="8" y="18" width="304" height="58" rx="4" />
      <circle className="ilustracao__traco" cx="30" cy="47" r="7" />
      <rect className="ilustracao__traco" x="50" y="40" width="14" height="14" rx="2" />
      <text className="ilustracao__texto" x="72" y="51">
        Desativar cache
      </text>
      <g className="ilustracao__pulo">
        <path className="ilustracao__traco ilustracao__traco--destaque" d="M276 36 v16 M269 46 l7 7 l7 -7" />
        <line className="ilustracao__traco ilustracao__traco--destaque" x1="267" y1="60" x2="285" y2="60" />
      </g>
      <rect className="ilustracao__traco" x="112" y="86" width="192" height="64" rx="4" />
      <rect className="ilustracao__realce" x="118" y="92" width="180" height="24" rx="3" />
      <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="128" y="108">
        Exportar HAR (sanitized)
      </text>
      <text className="ilustracao__texto" x="128" y="136">
        Exportar HAR (completo)
      </text>
      <path className="ilustracao__traco ilustracao__traco--destaque" d="M26 96 h34 l12 12 v50 h-46 z M60 96 v12 h12" />
      <text className="ilustracao__texto ilustracao__texto--forte" x="24" y="176">
        site.har
      </text>
    </>
  );
}
