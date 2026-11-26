import Janela from "../pecas/Janela.tsx";
import MiniaturaDaPaginaComLinks from "./MiniaturaDaPaginaComLinks.tsx";
import Robo from "../pecas/Robo.tsx";

const CONTADORES = [1, 2, 3];

export default function MiniaturaDoRoboNavegando() {
  return (
    <Janela tamanho="pequeno">
      <MiniaturaDaPaginaComLinks />
      <Robo x={16} y={22} tamanho="pequeno" />
      {CONTADORES.map((numero) => (
        <text
          key={numero}
          className={`modo-anim__texto modo-anim__texto--mono modo-anim__texto--destaque modo-anim__contador modo-anim__contador--${numero}`}
          x="46"
          y="52"
        >
          {numero}/20
        </text>
      ))}
    </Janela>
  );
}
