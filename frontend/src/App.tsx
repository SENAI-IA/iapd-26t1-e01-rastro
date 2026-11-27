import { useRef, useState } from "react";
import "./App.css";
import type { Acao, Relatorio } from "./relatorio/tiposDoRelatorio.ts";
import type { OrigemDoDado, Aba } from "./telas/tiposDaTela.ts";
import AvisoDeLimitacoes from "./moldura/AvisoDeLimitacoes.tsx";
import BarraDeFoco from "./moldura/BarraDeFoco.tsx";
import BarraSuperior from "./moldura/BarraSuperior.tsx";
import GuiaComoUsar from "./guia/GuiaComoUsar.tsx";
import JanelaDaTarefa from "./zonas/agir/JanelaDaTarefa.tsx";
import PainelOrigemDoDado from "./janelas/PainelOrigemDoDado.tsx";
import PainelDaSegurancaAtiva from "./segurancaAtiva/PainelDaSegurancaAtiva.tsx";
import TelaDoPainel from "./telas/TelaDoPainel.tsx";
import TourGuiado from "./janelas/TourGuiado.tsx";
import { PASSOS_DO_TOUR, type PassoDoTour } from "./conteudo/tour.ts";
import { idDoItemDaBiblioteca } from "./calculosDeTela/identificadores.ts";
import { rolarAteOElemento } from "./calculosDeTela/rolagem.ts";
import { depoisDeDesenhar } from "./calculosDeTela/desenho.ts";
import { usarModoFoco } from "./hooks/usarModoFoco.ts";
import { usarTema } from "./hooks/usarTema.ts";

interface Props {
  relatorio: Relatorio | null;
}

function passosQueExistemNaTela(): PassoDoTour[] {
  return PASSOS_DO_TOUR.filter((passo) => document.querySelector(passo.seletor) !== null);
}

function abrirBiblioteca(id: string, cabecalhoFixo: HTMLElement | null) {
  const itemDaBiblioteca = document.getElementById(idDoItemDaBiblioteca(id));
  if (!itemDaBiblioteca) {
    return;
  }
  itemDaBiblioteca.querySelector("details")?.setAttribute("open", "");
  rolarAteOElemento(itemDaBiblioteca, cabecalhoFixo?.offsetHeight ?? 0, "smooth");
  itemDaBiblioteca.querySelector<HTMLElement>("summary")?.focus({ preventScroll: true });
}

export default function App({ relatorio }: Props) {
  const cabecalhoFixo = useRef<HTMLDivElement>(null);
  const { tema, trocarTema } = usarTema();
  const { zonaEmFoco, entrarNoFoco, sairDoFoco, sairDoFocoSemVoltarAZona } = usarModoFoco(cabecalhoFixo);
  const [abaAtual, setAbaAtual] = useState<Aba>(relatorio ? "painel" : "como-usar");
  const [origemAberta, setOrigemAberta] = useState<OrigemDoDado | null>(null);
  const [tarefaAberta, setTarefaAberta] = useState<Acao | null>(null);
  const [passosDoTour, setPassosDoTour] = useState<PassoDoTour[] | null>(null);

  const medirAlturaDoCabecalhoFixo = () => cabecalhoFixo.current?.offsetHeight ?? 0;

  const trocarAba = (novaAba: Aba) => {
    sairDoFocoSemVoltarAZona();
    setAbaAtual(novaAba);
    window.scrollTo({ top: 0 });
  };

  const abrirTour = () => {
    sairDoFocoSemVoltarAZona();
    setAbaAtual("painel");
    depoisDeDesenhar(() => setPassosDoTour(passosQueExistemNaTela()));
  };

  const irParaBiblioteca = (id: string) => {
    sairDoFocoSemVoltarAZona();
    depoisDeDesenhar(() => abrirBiblioteca(id, cabecalhoFixo.current));
  };

  const conteudoDaAba = () => {
    if (abaAtual === "como-usar") {
      return (
        <GuiaComoUsar
          aoIrParaOPainel={relatorio ? () => trocarAba("painel") : null}
          medirAlturaDoCabecalhoFixo={medirAlturaDoCabecalhoFixo}
        />
      );
    }
    if (relatorio === null) {
      return <p>Este arquivo não traz os dados de uma análise. Gere o relatório com o Rastro: veja em "Como usar".</p>;
    }
    if (abaAtual === "pentest" && relatorio.pentest) {
      return <PainelDaSegurancaAtiva pentest={relatorio.pentest} />;
    }
    return (
      <TelaDoPainel
        relatorio={relatorio}
        zonaEmFoco={zonaEmFoco}
        aoFocar={entrarNoFoco}
        aoIrParaBiblioteca={irParaBiblioteca}
        aoAbrirTarefa={setTarefaAberta}
        aoVerOrigem={setOrigemAberta}
      />
    );
  };

  return (
    <>
      <div className="app__cabecalho-fixo" ref={cabecalhoFixo}>
        <BarraSuperior
          tema={tema}
          abaAtual={abaAtual}
          aoTrocarTema={trocarTema}
          aoTrocarAba={trocarAba}
          aoAbrirTour={relatorio ? abrirTour : null}
          relatorio={relatorio}
        />
        {relatorio && zonaEmFoco && (
          <BarraDeFoco zonaEmFoco={zonaEmFoco} aoTrocarZona={entrarNoFoco} aoSair={sairDoFoco} />
        )}
        {relatorio && abaAtual === "painel" && relatorio.analise.limitacoes.length > 0 && (
          <AvisoDeLimitacoes analise={relatorio.analise} recolhido={zonaEmFoco !== null || passosDoTour !== null} />
        )}
      </div>
      <main className={zonaEmFoco ? "app app--foco" : "app"}>{conteudoDaAba()}</main>
      {origemAberta && <PainelOrigemDoDado origem={origemAberta} aoFechar={() => setOrigemAberta(null)} />}
      {tarefaAberta && <JanelaDaTarefa acao={tarefaAberta} aoFechar={() => setTarefaAberta(null)} />}
      {passosDoTour && passosDoTour.length > 0 && (
        <TourGuiado passos={passosDoTour} cabecalhoFixo={cabecalhoFixo.current} aoFechar={() => setPassosDoTour(null)} />
      )}
    </>
  );
}
