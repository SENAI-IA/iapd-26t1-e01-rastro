import type { Acao, Resumo } from "../tipos.ts";
import Indicador from "./Indicador.tsx";
import Selo from "./Selo.tsx";
import SeloDePrioridade from "./SeloDePrioridade.tsx";
import { formatarNota, plural } from "./formato.ts";
import "./Indicadores.css";

interface Props {
  resumo: Resumo;
  primeiraAcao: Acao | undefined;
}

export default function Indicadores({ resumo, primeiraAcao }: Props) {
  return (
    <section className="indicadores" aria-label="Indicadores">
      <Indicador
        titulo="Risco do site"
        icone="alvo"
        valor={resumo.nota_maxima === null ? "–" : formatarNota(resumo.nota_maxima)}
        complemento={resumo.nota_maxima === null ? undefined : "/ 10"}
        descricao={
          resumo.nota_maxima === null
            ? "Nenhuma falha com nota nesta gravação."
            : "Maior nota entre as falhas encontradas nas bibliotecas."
        }
      />
      <Indicador
        titulo="Bibliotecas vulneráveis"
        icone="pacote"
        valor={String(resumo.bibliotecas_vulneraveis)}
        complemento={`de ${resumo.bibliotecas}`}
        descricao={descreverBibliotecas(resumo)}
      />
      <Indicador
        titulo="Encontradas só pela IA"
        icone="ia"
        valor={resumo.encontradas_so_pela_ia === null ? "–" : String(resumo.encontradas_so_pela_ia)}
        selo={
          <Selo tom="ia" icone="ia">
            IA
          </Selo>
        }
        descricao="Bibliotecas escondidas em bundles, que só a IA reconheceu."
      />
      <Indicador
        titulo="Primeira ação"
        icone="octogono"
        valor={String(resumo.acoes)}
        complemento={resumo.acoes === 1 ? "ação no plano" : "ações no plano"}
        selo={primeiraAcao && <SeloDePrioridade prioridade={primeiraAcao.prioridade} />}
        descricao={
          primeiraAcao ? (
            <>
              Comece por: <strong>{primeiraAcao.o_que_fazer}</strong>.
            </>
          ) : (
            "Nada a corrigir nesta gravação."
          )
        }
      />
    </section>
  );
}

function descreverBibliotecas(resumo: Resumo): string {
  const partes = [plural(resumo.achados, "falha conhecida", "falhas conhecidas")];
  if (resumo.bibliotecas_nao_consultadas > 0) {
    partes.push(plural(resumo.bibliotecas_nao_consultadas, "não consultada", "não consultadas"));
  }
  if (resumo.bibliotecas_a_confirmar > 0) {
    partes.push(`${resumo.bibliotecas_a_confirmar} a confirmar`);
  }
  return partes.join(" · ");
}
