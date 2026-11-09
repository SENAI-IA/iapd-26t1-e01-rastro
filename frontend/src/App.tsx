import { useEffect, useState } from "react";
import "./App.css";
import type { Relatorio } from "./tipos.ts";
import AvisoSemIA from "./componentes/AvisoSemIA.tsx";
import BarraSuperior, { type Tema } from "./componentes/BarraSuperior.tsx";
import CabecalhoAnalise from "./componentes/CabecalhoAnalise.tsx";
import Indicadores from "./componentes/Indicadores.tsx";
import ListaAConfirmar from "./componentes/ListaAConfirmar.tsx";
import ListaBibliotecas from "./componentes/ListaBibliotecas.tsx";
import ListaChecagens from "./componentes/ListaChecagens.tsx";
import PlanoDeAcao from "./componentes/PlanoDeAcao.tsx";

interface Props {
  relatorio: Relatorio | null;
}

function temaDoSistema(): Tema {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "escuro" : "claro";
}

export default function App({ relatorio }: Props) {
  const [temaEscolhido, setTemaEscolhido] = useState<Tema | null>(null);
  const tema = temaEscolhido ?? temaDoSistema();

  useEffect(() => {
    if (temaEscolhido) {
      document.documentElement.dataset.tema = temaEscolhido;
    }
  }, [temaEscolhido]);

  const trocarTema = () => setTemaEscolhido(tema === "claro" ? "escuro" : "claro");

  return (
    <>
      <div className="app__topo">
        <BarraSuperior tema={tema} aoTrocarTema={trocarTema} />
        {relatorio && relatorio.analise.limitacoes.length > 0 && <AvisoSemIA analise={relatorio.analise} />}
      </div>
      <main className="app">
        {relatorio === null ? (
          <p>Este arquivo não traz os dados de uma análise. Gere o relatório com o Rastro.</p>
        ) : (
          <>
            <CabecalhoAnalise analise={relatorio.analise} />
            <Indicadores resumo={relatorio.resumo} primeiraAcao={relatorio.plano_de_acao[0]} />
            <PlanoDeAcao acoes={relatorio.plano_de_acao} />
            <ListaBibliotecas bibliotecas={relatorio.bibliotecas} achados={relatorio.achados} />
            {relatorio.a_confirmar.length > 0 && (
              <ListaAConfirmar bibliotecas={relatorio.a_confirmar} travasAcionadas={relatorio.ia.travas_acionadas} />
            )}
            <ListaChecagens
              checagens={relatorio.checagens}
              comFalha={relatorio.resumo.checagens_com_falha}
              naoVerificadas={relatorio.resumo.checagens_nao_verificadas}
            />
          </>
        )}
      </main>
    </>
  );
}
