import { useEffect, useRef, useState, type ReactNode } from "react";
import "./App.css";
import type { Acao, Relatorio } from "./tipos.ts";
import { idDaZona, ZONAS, type NomeDaZona } from "./dados/zonas.ts";
import AvisoSemIA from "./componentes/AvisoSemIA.tsx";
import BarraDeFoco from "./componentes/BarraDeFoco.tsx";
import BarraSuperior, { type Tema } from "./componentes/BarraSuperior.tsx";
import CabecalhoAnalise from "./componentes/CabecalhoAnalise.tsx";
import Indicadores from "./componentes/Indicadores.tsx";
import ListaAConfirmar from "./componentes/ListaAConfirmar.tsx";
import ListaBibliotecas from "./componentes/ListaBibliotecas.tsx";
import ListaChecagens from "./componentes/ListaChecagens.tsx";
import ModalTask from "./componentes/ModalTask.tsx";
import PainelOrigemDoDado, { type OrigemDoDado } from "./componentes/PainelOrigemDoDado.tsx";
import PlanoDeAcao from "./componentes/PlanoDeAcao.tsx";
import Zona from "./componentes/Zona.tsx";

interface Props {
  relatorio: Relatorio | null;
}

function temaDoSistema(): Tema {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "escuro" : "claro";
}

function algumDialogoAberto(): boolean {
  return document.querySelector("dialog[open]") !== null;
}

function rolarAteAZona(zona: NomeDaZona, topo: HTMLElement | null) {
  const elemento = document.getElementById(idDaZona(zona));
  if (!elemento) {
    return;
  }
  const alturaDoTopo = topo?.offsetHeight ?? 0;
  window.scrollTo({ top: elemento.getBoundingClientRect().top + window.scrollY - alturaDoTopo - 12 });
  elemento.querySelector<HTMLButtonElement>(".zona__focar")?.focus({ preventScroll: true });
}

export default function App({ relatorio }: Props) {
  const [temaEscolhido, setTemaEscolhido] = useState<Tema | null>(null);
  const tema = temaEscolhido ?? temaDoSistema();
  const [origemAberta, setOrigemAberta] = useState<OrigemDoDado | null>(null);
  const [taskAberta, setTaskAberta] = useState<Acao | null>(null);
  const [zonaEmFoco, setZonaEmFoco] = useState<NomeDaZona | null>(null);
  const zonaQueSaiuDoFoco = useRef<NomeDaZona | null>(null);
  const topo = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (temaEscolhido) {
      document.documentElement.dataset.tema = temaEscolhido;
    }
  }, [temaEscolhido]);

  useEffect(() => {
    if (zonaEmFoco !== null) {
      window.scrollTo({ top: 0 });
      return;
    }
    if (zonaQueSaiuDoFoco.current) {
      rolarAteAZona(zonaQueSaiuDoFoco.current, topo.current);
      zonaQueSaiuDoFoco.current = null;
    }
  }, [zonaEmFoco]);

  useEffect(() => {
    if (zonaEmFoco === null) {
      return;
    }
    const sairComEsc = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !evento.defaultPrevented && !algumDialogoAberto()) {
        zonaQueSaiuDoFoco.current = zonaEmFoco;
        setZonaEmFoco(null);
      }
    };
    document.addEventListener("keydown", sairComEsc);
    return () => document.removeEventListener("keydown", sairComEsc);
  }, [zonaEmFoco]);

  const trocarTema = () => setTemaEscolhido(tema === "claro" ? "escuro" : "claro");
  const sairDoFoco = () => {
    zonaQueSaiuDoFoco.current = zonaEmFoco;
    setZonaEmFoco(null);
  };

  const conteudoDaZona = (zona: NomeDaZona, relatorio: Relatorio): ReactNode => {
    switch (zona) {
      case "rastreado":
        return <Indicadores resumo={relatorio.resumo} primeiraAcao={relatorio.plano_de_acao[0]} />;
      case "agir":
        return <PlanoDeAcao acoes={relatorio.plano_de_acao} aoAbrirTask={setTaskAberta} />;
      case "detalhes":
        return (
          <>
            <ListaBibliotecas
              bibliotecas={relatorio.bibliotecas}
              achados={relatorio.achados}
              aoVerOrigem={setOrigemAberta}
            />
            {relatorio.a_confirmar.length > 0 && (
              <ListaAConfirmar bibliotecas={relatorio.a_confirmar} travasAcionadas={relatorio.ia.travas_acionadas} />
            )}
            <ListaChecagens
              checagens={relatorio.checagens}
              comFalha={relatorio.resumo.checagens_com_falha}
              naoVerificadas={relatorio.resumo.checagens_nao_verificadas}
            />
          </>
        );
    }
  };

  return (
    <>
      <div className="app__topo" ref={topo}>
        <BarraSuperior tema={tema} aoTrocarTema={trocarTema} />
        {relatorio && zonaEmFoco && (
          <BarraDeFoco zonaEmFoco={zonaEmFoco} aoTrocarZona={setZonaEmFoco} aoSair={sairDoFoco} />
        )}
        {relatorio && relatorio.analise.limitacoes.length > 0 && (
          <AvisoSemIA analise={relatorio.analise} recolhido={zonaEmFoco !== null} />
        )}
      </div>
      <main className={zonaEmFoco ? "app app--foco" : "app"}>
        {relatorio === null ? (
          <p>Este arquivo não traz os dados de uma análise. Gere o relatório com o Rastro.</p>
        ) : (
          <>
            {zonaEmFoco === null && <CabecalhoAnalise analise={relatorio.analise} />}
            {ZONAS.filter((zona) => zonaEmFoco === null || zona.id === zonaEmFoco).map((zona) => (
              <Zona key={zona.id} zona={zona} aoFocar={zonaEmFoco ? undefined : () => setZonaEmFoco(zona.id)}>
                {conteudoDaZona(zona.id, relatorio)}
              </Zona>
            ))}
          </>
        )}
      </main>
      {origemAberta && <PainelOrigemDoDado origem={origemAberta} aoFechar={() => setOrigemAberta(null)} />}
      {taskAberta && <ModalTask acao={taskAberta} aoFechar={() => setTaskAberta(null)} />}
    </>
  );
}
