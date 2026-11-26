interface Props {
  comando: string;
}

export default function MiniaturaDoTerminal({ comando }: Props) {
  return (
    <>
      <line className="animacao-do-modo__traco" x1="0" y1="11" x2="68" y2="11" />
      <text className="animacao-do-modo__texto animacao-do-modo__texto--mono animacao-do-modo__texto--forte" x="6" y="25">
        $ rastro
      </text>
      <text className="animacao-do-modo__texto animacao-do-modo__texto--mono animacao-do-modo__texto--forte" x="6" y="35">
        gravar
      </text>
      {comando && (
        <text className="animacao-do-modo__texto animacao-do-modo__texto--mono animacao-do-modo__texto--destaque animacao-do-modo__texto--forte" x="6" y="45">
          {comando}
        </text>
      )}
      <rect className="animacao-do-modo__cursor-texto" x={comando ? 40 : 6} y={39} width="4" height="7" />
    </>
  );
}
