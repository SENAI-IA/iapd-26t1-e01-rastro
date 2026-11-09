import type { DadosDaAnalise } from "../tipos.ts";
import Icone, { type NomeDoIcone } from "./Icone.tsx";
import "./AvisoSemIA.css";

interface Props {
  analise: DadosDaAnalise;
  recolhido?: boolean;
}

const ICONE_DA_LIMITACAO: Record<string, NomeDoIcone> = {
  bundles_nao_procurados: "pacote",
  achados_sem_explicacao: "ia",
  sem_javascript: "arquivo",
  ia_falhou_identificacao: "pacote",
  ia_falhou_explicacao: "ia",
};

export default function AvisoSemIA({ analise, recolhido = false }: Props) {
  const semIA = analise.ia === null;
  return (
    <aside className="aviso-sem-ia" aria-label="Limitações da análise">
      <details className="aviso-sem-ia__conteudo" open={!recolhido}>
        <summary className="aviso-sem-ia__titulo">
          <Icone nome="triangulo" tamanho={16} />
          {semIA ? "Análise sem IA: o resultado está incompleto." : "Análise incompleta."}
        </summary>
        <ul className="aviso-sem-ia__lista">
          {analise.limitacoes.map((limitacao) => (
            <li key={limitacao.id}>
              <Icone nome={ICONE_DA_LIMITACAO[limitacao.id] ?? "info"} />
              {limitacao.texto}
            </li>
          ))}
          {analise.continua_igual && (
            <li>
              <Icone nome="certo" />
              {analise.continua_igual}
            </li>
          )}
          {semIA && (
            <li>
              <Icone nome="terminal" />
              <span>
                Para a análise completa, rode com IA: <code>{comandoComIA(analise.har)}</code>
              </span>
            </li>
          )}
        </ul>
      </details>
    </aside>
  );
}

function comandoComIA(har: string): string {
  const arquivo = har.includes(" ") ? `"${har}"` : har;
  return `python -m rastro analisar ${arquivo}`;
}
