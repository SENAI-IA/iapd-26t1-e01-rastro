import AcoesDaBarra from "./AcoesDaBarra.tsx";
import BotaoDaAba from "./BotaoDaAba.tsx";
import Icone from "../basicos/Icone.tsx";
import type { Aba, Tema } from "../telas/tiposDaTela.ts";
import "./BarraSuperior.css";

interface Props {
  tema: Tema;
  abaAtual: Aba;
  aoTrocarTema: () => void;
  aoTrocarAba: (aba: Aba) => void;
  aoAbrirTour: (() => void) | null;
  temPentest: boolean;
}

export default function BarraSuperior({ tema, abaAtual, aoTrocarTema, aoTrocarAba, aoAbrirTour, temPentest }: Props) {
  return (
    <header className="barra-superior">
      <div className="barra-superior__conteudo">
        <span className="barra-superior__marca">
          <Icone nome="logo" tamanho={24} />
          rastro
        </span>
        <nav className="barra-superior__abas" aria-label="Telas do relatório">
          <BotaoDaAba aba="painel" abaAtual={abaAtual} icone="painel" aoTrocarAba={aoTrocarAba}>
            Painel
          </BotaoDaAba>
          {temPentest && (
            <BotaoDaAba
              aba="pentest"
              abaAtual={abaAtual}
              icone="lupa"
              classeExtra="barra-superior__aba--seguranca-ativa"
              aoTrocarAba={aoTrocarAba}
            >
              Segurança ativa
            </BotaoDaAba>
          )}
          <BotaoDaAba aba="como-usar" abaAtual={abaAtual} icone="livro" aoTrocarAba={aoTrocarAba}>
            Como usar
          </BotaoDaAba>
        </nav>
        <AcoesDaBarra tema={tema} aoTrocarTema={aoTrocarTema} aoAbrirTour={aoAbrirTour} />
      </div>
    </header>
  );
}
