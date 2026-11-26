import { CENTRO, RAIO_EXTERNO } from "../../calculosDeTela/geometriaDoRadar.ts";

export default function FundoDoRadar() {
  return (
    <>
      <defs>
        <radialGradient id="radar-fundo">
          <stop offset="0" className="radar__fundo-centro" />
          <stop offset="1" className="radar__fundo-borda" />
        </radialGradient>
      </defs>
      <circle className="radar__disco" cx={CENTRO.x} cy={CENTRO.y} r={RAIO_EXTERNO} fill="url(#radar-fundo)" />
    </>
  );
}
