import Icone from "./Icone.tsx";
import "./BarraSuperior.css";

export type Tema = "claro" | "escuro";
export type Tela = "painel" | "pentest" | "como-usar";

interface Props {
  tema: Tema;
  tela: Tela;
  aoTrocarTema: () => void;
  aoTrocarTela: (tela: Tela) => void;
  aoAbrirTour: (() => void) | null;
  temPentest: boolean;
}

export default function BarraSuperior({
  tema,
  tela,
  aoTrocarTema,
  aoTrocarTela,
  aoAbrirTour,
  temPentest,
}: Props) {
  const proximoTema = tema === "claro" ? "escuro" : "claro";
  return (
    <header className="barra-superior">
      <div className="barra-superior__conteudo">
        <span className="barra-superior__marca">
          <Icone nome="logo" tamanho={24} />
          rastro
        </span>
        <nav className="barra-superior__telas" aria-label="Telas do relatório">
          <button
            type="button"
            className="barra-superior__tela"
            aria-current={tela === "painel" ? "page" : undefined}
            onClick={() => aoTrocarTela("painel")}
          >
            <Icone nome="painel" />
            Painel
          </button>
          {temPentest && (
            <button
              type="button"
              className="barra-superior__tela"
              aria-current={tela === "pentest" ? "page" : undefined}
              onClick={() => aoTrocarTela("pentest")}
            >
              <Icone nome="lupa" />
              Pentest
            </button>
          )}
          <button
            type="button"
            className="barra-superior__tela"
            aria-current={tela === "como-usar" ? "page" : undefined}
            onClick={() => aoTrocarTela("como-usar")}
          >
            <Icone nome="livro" />
            Como usar
          </button>
        </nav>
        <div className="barra-superior__acoes">
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
      </div>
    </header>
  );
}
