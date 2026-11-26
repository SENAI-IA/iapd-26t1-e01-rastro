import type { ReactNode } from "react";
import type { Acao, Resumo } from "../../relatorio/tiposDoRelatorio.ts";
import Indicador from "./Indicador.tsx";
import Selo from "../../basicos/Selo.tsx";
import SeloDePrioridade from "../../basicos/SeloDePrioridade.tsx";
import { formatarNota, plural } from "../../formatacao/formato.ts";
import Termo from "../../basicos/Termo.tsx";
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
        descricao={descreverRisco(resumo)}
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
        valor={resumo.encontradas_so_pela_ia === null ? "Não procurado" : String(resumo.encontradas_so_pela_ia)}
        selo={
          <Selo tom="ia" icone="ia">
            IA
          </Selo>
        }
        descricao={descreverSoPelaIA(resumo)}
      />
      <Indicador
        titulo="Primeira ação"
        icone="octogono"
        valor={String(resumo.acoes)}
        complemento={resumo.acoes === 1 ? "ação no plano" : "ações no plano"}
        selo={primeiraAcao && <SeloDePrioridade prioridade={primeiraAcao.prioridade} />}
        descricao={descreverPrimeiraAcao(primeiraAcao)}
      />
    </section>
  );
}

function descreverRisco(resumo: Resumo): string {
  if (resumo.nota_maxima === null) {
    return "Nenhuma falha com nota nesta gravação.";
  }
  return "Maior nota entre as falhas encontradas nas bibliotecas.";
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

function descreverSoPelaIA(resumo: Resumo): ReactNode {
  if (resumo.encontradas_so_pela_ia === null) {
    return (
      <>
        Análise sem IA: bibliotecas escondidas em <Termo nome="Bundle">bundles</Termo> não foram procuradas.
      </>
    );
  }
  return (
    <>
      Bibliotecas escondidas em <Termo nome="Bundle">bundles</Termo>, que só a IA reconheceu.
    </>
  );
}

function descreverPrimeiraAcao(primeiraAcao: Acao | undefined): ReactNode {
  if (!primeiraAcao) {
    return "Nada a corrigir nesta gravação.";
  }
  return (
    <>
      Comece por: <strong>{primeiraAcao.o_que_fazer}</strong>.
    </>
  );
}
