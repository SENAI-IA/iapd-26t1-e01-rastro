import Icone from "../basicos/Icone.tsx";
import type { Relatorio } from "../relatorio/tiposDoRelatorio.ts";
import MenuDeBaixar from "./MenuDeBaixar.tsx";
import type { Tema } from "../telas/tiposDaTela.ts";

interface Props {
  tema: Tema;
  aoTrocarTema: () => void;
  aoAbrirTour: (() => void) | null;
  relatorio: Relatorio | null;
}

export default function AcoesDaBarra({ tema, aoTrocarTema, aoAbrirTour, relatorio }: Props) {
  const proximoTema = tema === "claro" ? "escuro" : "claro";
  return (
    <div className="barra-superior__acoes">
      {relatorio && <MenuDeBaixar relatorio={relatorio} />}
      {aoAbrirTour && (
        <button
          type="button"
          className="barra-superior__tour"
          onClick={aoAbrirTour}
          aria-label="Tour guiado pelo relatório"
          title="Tour guiado pelo relatório"
        >
          <Icone nome="bussola" tamanho={16} />
          <span className="barra-superior__rotulo">Tour guiado</span>
        </button>
      )}
      <button
        type="button"
        className="barra-superior__tema"
        onClick={aoTrocarTema}
        aria-label={`Mudar para o tema ${proximoTema}`}
        title={`Mudar para o tema ${proximoTema}`}
      >
        <Icone nome={tema === "claro" ? "lua" : "sol"} tamanho={16} />
      </button>
    </div>
  );
}
