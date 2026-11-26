import type { Camada, PassoDaVisita } from "../../relatorio/tiposDoRelatorio.ts";
import { CENTRO, RAIO_DA_CAMADA } from "../../calculosDeTela/geometriaDoRadar.ts";

const NOME_DA_CAMADA: Record<Camada, string> = {
  pagina: "páginas HTML",
  script: "scripts JS",
  estilo: "estilos CSS",
  dados: "dados e APIs",
  midia: "imagens e fontes",
};
const CAMADAS: Camada[] = ["pagina", "script", "estilo", "dados", "midia"];
const ALTURA_DO_NOME_NO_ANEL = 3.5;

interface Props {
  passos: PassoDaVisita[];
  camadasComFalha: Set<Camada>;
}

export default function AneisDoRadar({ passos, camadasComFalha }: Props) {
  return (
    <>
      {CAMADAS.map((camada) => (
        <g key={camada} className={camadasComFalha.has(camada) ? "radar__camada radar__camada--com-falha" : "radar__camada"}>
          <circle className="radar__anel" cx={CENTRO.x} cy={CENTRO.y} r={RAIO_DA_CAMADA[camada]} />
          <text className="radar__nome-da-camada" x={CENTRO.x} y={CENTRO.y - RAIO_DA_CAMADA[camada] + ALTURA_DO_NOME_NO_ANEL}>
            {NOME_DA_CAMADA[camada]} · {passos.filter((passo) => passo.camada === camada).length}
          </text>
        </g>
      ))}
    </>
  );
}
