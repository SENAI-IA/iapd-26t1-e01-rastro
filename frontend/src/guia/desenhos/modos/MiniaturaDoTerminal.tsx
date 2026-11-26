interface Props {
  comando: string;
}

export default function MiniaturaDoTerminal({ comando }: Props) {
  return (
    <>
      <line className="modo-anim__traco" x1="0" y1="11" x2="68" y2="11" />
      <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--forte" x="6" y="25">
        $ rastro
      </text>
      <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--forte" x="6" y="35">
        gravar
      </text>
      {comando && (
        <text className="modo-anim__texto modo-anim__texto--mono modo-anim__texto--destaque modo-anim__texto--forte" x="6" y="45">
          {comando}
        </text>
      )}
      <rect className="modo-anim__cursor-texto" x={comando ? 40 : 6} y={39} width="4" height="7" />
    </>
  );
}
