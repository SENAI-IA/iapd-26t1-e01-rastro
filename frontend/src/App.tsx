import { useRef, useState } from "react";
import "./App.css";
import type { Acao, Relatorio } from "./relatorio/tiposDoRelatorio.ts";
import type { OrigemDoDado, Tela } from "./telas/tiposDaTela.ts";
import AvisoSemIA from "./moldura/AvisoSemIA.tsx";
import BarraDeFoco from "./moldura/BarraDeFoco.tsx";
import BarraSuperior from "./moldura/BarraSuperior.tsx";
import GuiaComoUsar from "./guia/GuiaComoUsar.tsx";
import ModalTask from "./zonas/agir/ModalTask.tsx";
import PainelOrigemDoDado from "./janelas/PainelOrigemDoDado.tsx";
import PainelPentest from "./segurancaAtiva/PainelPentest.tsx";
import TelaDoPainel from "./telas/TelaDoPainel.tsx";
import TourGuiado from "./janelas/TourGuiado.tsx";
import { PASSOS_DO_TOUR, type PassoDoTour } from "./conteudo/tour.ts";
import { idDaLinhaDaBiblioteca } from "./calculosDeTela/identificadores.ts";
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
  const linha = document.getElementById(idDaLinhaDaBiblioteca(id));
  if (!linha) {
    return;
  }
  linha.querySelector("details")?.setAttribute("open", "");
  rolarAteOElemento(linha, cabecalhoFixo?.offsetHeight ?? 0, "smooth");
  linha.querySelector<HTMLElement>("summary")?.focus({ preventScroll: true });
}

export default function App({ relatorio }: Props) {
  const cabecalhoFixo = useRef<HTMLDivElement>(null);
  const { tema, trocarTema } = usarTema();
  const { zonaEmFoco, entrarNoFoco, sairDoFoco, sairDoFocoSemVoltarAZona } = usarModoFoco(cabecalhoFixo);
  const [tela, setTela] = useState<Tela>(relatorio ? "painel" : "como-usar");
  const [origemAberta, setOrigemAberta] = useState<OrigemDoDado | null>(null);
  const [taskAberta, setTaskAberta] = useState<Acao | null>(null);
  const [passosDoTour, setPassosDoTour] = useState<PassoDoTour[] | null>(null);

  const medirAlturaDoCabecalhoFixo = () => cabecalhoFixo.current?.offsetHeight ?? 0;

  const trocarTela = (novaTela: Tela) => {
    sairDoFocoSemVoltarAZona();
    setTela(novaTela);
    window.scrollTo({ top: 0 });
  };

  const abrirTour = () => {
    sairDoFocoSemVoltarAZona();
    setTela("painel");
    depoisDeDesenhar(() => setPassosDoTour(passosQueExistemNaTela()));
  };

  const irParaBiblioteca = (id: string) => {
    sairDoFocoSemVoltarAZona();
    depoisDeDesenhar(() => abrirBiblioteca(id, cabecalhoFixo.current));
  };

  const conteudoDaAba = () => {
    if (tela === "como-usar") {
      return (
        <GuiaComoUsar
          aoIrParaOPainel={relatorio ? () => trocarTela("painel") : null}
          medirAlturaDoCabecalhoFixo={medirAlturaDoCabecalhoFixo}
        />
      );
    }
    if (relatorio === null) {
      return <p>Este arquivo não traz os dados de uma análise. Gere o relatório com o Rastro: veja em "Como usar".</p>;
    }
    if (tela === "pentest" && relatorio.pentest) {
      return <PainelPentest pentest={relatorio.pentest} />;
    }
    return (
      <TelaDoPainel
        relatorio={relatorio}
        zonaEmFoco={zonaEmFoco}
        aoFocar={entrarNoFoco}
        aoIrParaBiblioteca={irParaBiblioteca}
        aoAbrirTask={setTaskAberta}
        aoVerOrigem={setOrigemAberta}
      />
    );
  };

  return (
    <>
      <div className="app__topo" ref={cabecalhoFixo}>
        <BarraSuperior
          tema={tema}
          tela={tela}
          aoTrocarTema={trocarTema}
          aoTrocarTela={trocarTela}
          aoAbrirTour={relatorio ? abrirTour : null}
          temPentest={relatorio?.pentest != null}
        />
        {relatorio && zonaEmFoco && (
          <BarraDeFoco zonaEmFoco={zonaEmFoco} aoTrocarZona={entrarNoFoco} aoSair={sairDoFoco} />
        )}
        {relatorio && tela === "painel" && relatorio.analise.limitacoes.length > 0 && (
          <AvisoSemIA analise={relatorio.analise} recolhido={zonaEmFoco !== null || passosDoTour !== null} />
        )}
      </div>
      <main className={zonaEmFoco ? "app app--foco" : "app"}>{conteudoDaAba()}</main>
      {origemAberta && <PainelOrigemDoDado origem={origemAberta} aoFechar={() => setOrigemAberta(null)} />}
      {taskAberta && <ModalTask acao={taskAberta} aoFechar={() => setTaskAberta(null)} />}
      {passosDoTour && passosDoTour.length > 0 && (
        <TourGuiado passos={passosDoTour} topo={cabecalhoFixo.current} aoFechar={() => setPassosDoTour(null)} />
      )}
    </>
  );
}
