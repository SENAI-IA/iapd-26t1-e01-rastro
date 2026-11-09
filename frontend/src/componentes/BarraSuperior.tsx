import Icone from "./Icone.tsx";
import "./BarraSuperior.css";

export type Tema = "claro" | "escuro";

interface Props {
  tema: Tema;
  aoTrocarTema: () => void;
}

export default function BarraSuperior({ tema, aoTrocarTema }: Props) {
  const proximoTema = tema === "claro" ? "escuro" : "claro";
  return (
    <header className="barra-superior">
      <div className="barra-superior__conteudo">
        <span className="barra-superior__marca">
          <Icone nome="logo" tamanho={24} />
          rastro
        </span>
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
    </header>
  );
}
