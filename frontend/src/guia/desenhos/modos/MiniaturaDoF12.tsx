import Janela from "../pecas/Janela.tsx";

export default function MiniaturaDoF12() {
  return (
    <Janela tamanho="pequeno">
      <line className="animacao-do-modo__traco" x1="0" y1="30" x2="68" y2="30" />
      <line className="animacao-do-modo__linha" pathLength="1" x1="6" y1="38" x2="56" y2="38" />
      <line className="animacao-do-modo__linha animacao-do-modo__linha--2" pathLength="1" x1="6" y1="45" x2="44" y2="45" />
      <g className="animacao-do-modo__tecla">
        <rect className="animacao-do-modo__traco animacao-do-modo__traco--destaque" x="22" y="14" width="24" height="12" rx="2" />
        <text className="animacao-do-modo__texto animacao-do-modo__texto--destaque animacao-do-modo__texto--forte" x="27" y="23">
          F12
        </text>
      </g>
    </Janela>
  );
}
