export default function TerminalEsperandoOEnter() {
  return (
    <>
      <rect className="ilustracao__traco" x="192" y="18" width="120" height="154" rx="4" />
      <line className="ilustracao__traco" x1="192" y1="42" x2="312" y2="42" />
      <text className="ilustracao__texto" x="204" y="33.5">
        Terminal
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--1" x="202" y="64">
        Entre e aperte
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--1" x="202" y="78">
        Enter.
      </text>
      <g className="ilustracao__digita ilustracao__digita--4">
        <g className="ilustracao__tecla">
          <rect className="ilustracao__traco ilustracao__traco--destaque" x="216" y="94" width="72" height="28" rx="4" />
          <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="238" y="112.5">
            Enter
          </text>
        </g>
      </g>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--5"
        x="202"
        y="150"
      >
        [1/20] /
      </text>
    </>
  );
}
