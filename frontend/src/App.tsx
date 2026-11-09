import { useEffect, useState } from "react";
import "./App.css";
import type { Relatorio } from "./tipos.ts";
import BarraSuperior, { type Tema } from "./componentes/BarraSuperior.tsx";
import CabecalhoAnalise from "./componentes/CabecalhoAnalise.tsx";
import Indicadores from "./componentes/Indicadores.tsx";
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
      <BarraSuperior tema={tema} aoTrocarTema={trocarTema} />
      <main className="app">
        {relatorio === null ? (
          <p>Este arquivo não traz os dados de uma análise. Gere o relatório com o Rastro.</p>
        ) : (
          <>
            <CabecalhoAnalise analise={relatorio.analise} />
            <Indicadores resumo={relatorio.resumo} primeiraAcao={relatorio.plano_de_acao[0]} />
            <PlanoDeAcao acoes={relatorio.plano_de_acao} />
          </>
        )}
      </main>
    </>
  );
}
