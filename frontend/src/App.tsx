import "./App.css";
import type { Relatorio } from "./tipos.ts";

interface Props {
  relatorio: Relatorio | null;
}

export default function App({ relatorio }: Props) {
  if (relatorio === null) {
    return (
      <main className="app">
        <h1>Rastro</h1>
        <p>Este arquivo não traz os dados de uma análise. Gere o relatório com o Rastro.</p>
      </main>
    );
  }

  return (
    <main className="app">
      <h1>Rastro</h1>
      <p>
        {relatorio.analise.site ?? relatorio.analise.har} · {relatorio.analise.data}
      </p>
    </main>
  );
}
