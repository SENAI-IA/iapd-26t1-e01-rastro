import Janela from "../pecas/Janela.tsx";

export default function MiniaturaDoF12() {
  return (
    <Janela tamanho="pequeno">
      <line className="modo-anim__traco" x1="0" y1="30" x2="68" y2="30" />
      <line className="modo-anim__linha" pathLength="1" x1="6" y1="38" x2="56" y2="38" />
      <line className="modo-anim__linha modo-anim__linha--2" pathLength="1" x1="6" y1="45" x2="44" y2="45" />
      <g className="modo-anim__tecla">
        <rect className="modo-anim__traco modo-anim__traco--destaque" x="22" y="14" width="24" height="12" rx="2" />
        <text className="modo-anim__texto modo-anim__texto--destaque modo-anim__texto--forte" x="27" y="23">
          F12
        </text>
      </g>
    </Janela>
  );
}
