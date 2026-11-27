import { useState } from "react";
import { SIMULACOES_DO_GUIA, type TerminalDoGuia } from "../conteudo/simulacoesDoGuia.ts";
import PreviaDoTerminal from "./PreviaDoTerminal.tsx";
import SimulacaoNoTerminal from "./SimulacaoNoTerminal.tsx";
import "./TerminalDoPasso.css";

interface Props {
  terminal: TerminalDoGuia;
  simulando: boolean;
  aoSimular: () => void;
  aoFechar: () => void;
}

export default function TerminalDoPasso({ terminal, simulando, aoSimular, aoFechar }: Props) {
  const [fechouPeloBotao, setFechouPeloBotao] = useState(false);
  const simulacao = SIMULACOES_DO_GUIA[terminal];
  const fechar = () => {
    setFechouPeloBotao(true);
    aoFechar();
  };
  const simular = () => {
    setFechouPeloBotao(false);
    aoSimular();
  };
  if (simulando) {
    return <SimulacaoNoTerminal linhas={simulacao.completa} aoFechar={fechar} />;
  }
  return <PreviaDoTerminal linhas={simulacao.previa} aoSimular={simular} focarNoBotao={fechouPeloBotao} />;
}
