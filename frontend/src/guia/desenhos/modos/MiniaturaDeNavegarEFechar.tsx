import Cursor from "../pecas/Cursor.tsx";
import Janela from "../pecas/Janela.tsx";
import MiniaturaDaPaginaComLinks from "./MiniaturaDaPaginaComLinks.tsx";

export default function MiniaturaDeNavegarEFechar() {
  return (
    <Janela tamanho="pequeno">
      <MiniaturaDaPaginaComLinks />
      <g transform="translate(14 21)">
        <g className="modo-anim__passeio">
          <Cursor x={0} y={0} tamanho="pequeno" animacao="modo-anim__seta" />
        </g>
      </g>
      <g className="modo-anim__fechar">
        <path className="modo-anim__traco modo-anim__traco--destaque" d="M58 3.5 l5 5 M63 3.5 l-5 5" />
      </g>
    </Janela>
  );
}
