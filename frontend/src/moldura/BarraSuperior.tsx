import AcoesDaBarra from "./AcoesDaBarra.tsx";
import BotaoDaAba from "./BotaoDaAba.tsx";
import Icone from "../basicos/Icone.tsx";
import type { Tela, Tema } from "../telas/tiposDaTela.ts";
import "./BarraSuperior.css";

interface Props {
  tema: Tema;
  tela: Tela;
  aoTrocarTema: () => void;
  aoTrocarTela: (tela: Tela) => void;
  aoAbrirTour: (() => void) | null;
  temPentest: boolean;
}

export default function BarraSuperior({ tema, tela, aoTrocarTema, aoTrocarTela, aoAbrirTour, temPentest }: Props) {
  return (
    <header className="barra-superior">
      <div className="barra-superior__conteudo">
        <span className="barra-superior__marca">
          <Icone nome="logo" tamanho={24} />
          rastro
        </span>
        <nav className="barra-superior__telas" aria-label="Telas do relatório">
          <BotaoDaAba tela="painel" telaAberta={tela} icone="painel" aoTrocarTela={aoTrocarTela}>
            Painel
          </BotaoDaAba>
          {temPentest && (
            <BotaoDaAba
              tela="pentest"
              telaAberta={tela}
              icone="lupa"
              classeExtra="barra-superior__tela--pentest"
              aoTrocarTela={aoTrocarTela}
            >
              Segurança ativa
            </BotaoDaAba>
          )}
          <BotaoDaAba tela="como-usar" telaAberta={tela} icone="livro" aoTrocarTela={aoTrocarTela}>
            Como usar
          </BotaoDaAba>
        </nav>
        <AcoesDaBarra tema={tema} aoTrocarTema={aoTrocarTema} aoAbrirTour={aoAbrirTour} />
      </div>
    </header>
  );
}
