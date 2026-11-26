import Cursor from "../pecas/Cursor.tsx";
import Janela from "../pecas/Janela.tsx";
import LinhasQueAparecem from "../pecas/LinhasQueAparecem.tsx";
import MenuDeLinks from "../pecas/MenuDeLinks.tsx";

export default function DesenhoDeNavegar() {
  return (
    <Janela tamanho="grande">
      <MenuDeLinks tamanho="grande" />
      <rect className="ilustracao__traco ilustracao__traco--suave" x="24" y="70" width="272" height="30" rx="3" />
      <Cursor x={60} y={52} tamanho="medio" animacao="ilustracao__passeio" />
      <line className="ilustracao__traco" x1="8" y1="110" x2="312" y2="110" />
      <LinhasQueAparecem primeiraLinha={126} comprimentos={[210, 250, 180, 230]} />
    </Janela>
  );
}
