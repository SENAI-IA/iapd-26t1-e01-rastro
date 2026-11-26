import Cursor from "../pecas/Cursor.tsx";
import Janela from "../pecas/Janela.tsx";
import MiniaturaDaPaginaComLinks from "./MiniaturaDaPaginaComLinks.tsx";

export default function MiniaturaDeNavegarEFechar() {
  return (
    <Janela tamanho="pequeno">
      <MiniaturaDaPaginaComLinks />
      <g transform="translate(14 21)">
        <g className="animacao-do-modo__passeio">
          <Cursor x={0} y={0} tamanho="pequeno" animacao="animacao-do-modo__seta" />
        </g>
      </g>
      <g className="animacao-do-modo__fechar">
        <path className="animacao-do-modo__traco animacao-do-modo__traco--destaque" d="M58 3.5 l5 5 M63 3.5 l-5 5" />
      </g>
    </Janela>
  );
}
