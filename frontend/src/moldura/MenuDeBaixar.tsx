import { useId, useRef } from "react";
import Icone from "../basicos/Icone.tsx";
import { baixarArquivo, planilhaDeFalhas, relatorioCompleto, type ArquivoParaBaixar } from "../exportacao/arquivosParaBaixar.ts";
import { comPlural } from "../formatacao/formato.ts";
import { usarMenuAberto } from "../hooks/usarMenuAberto.ts";
import type { Relatorio } from "../relatorio/tiposDoRelatorio.ts";
import OpcaoDeBaixar from "./OpcaoDeBaixar.tsx";
import "./MenuDeBaixar.css";

interface Props {
  relatorio: Relatorio;
}

function descricaoDaPlanilha(falhas: number): string {
  if (falhas === 0) {
    return "Nenhuma falha conhecida: a planilha sai só com o cabeçalho.";
  }
  return `${comPlural(falhas, "falha conhecida", "falhas conhecidas")}, uma por linha, com nota, prioridade e versão corrigida.`;
}

export default function MenuDeBaixar({ relatorio }: Props) {
  const caixa = useRef<HTMLDivElement>(null);
  const menu = usarMenuAberto(caixa);
  const idDaLista = useId();
  const baixar = (arquivo: ArquivoParaBaixar) => {
    baixarArquivo(arquivo);
    menu.fechar();
  };

  return (
    <div className="menu-de-baixar" ref={caixa}>
      <button
        type="button"
        className="menu-de-baixar__botao"
        onClick={menu.alternar}
        aria-expanded={menu.aberto}
        aria-controls={idDaLista}
        title="Baixar a planilha de falhas ou o relatório completo"
      >
        <Icone nome="baixar" tamanho={16} />
        <span className="barra-superior__rotulo">Baixar</span>
      </button>
      {menu.aberto && (
        <div className="menu-de-baixar__lista" id={idDaLista}>
          <OpcaoDeBaixar
            titulo="Falhas das bibliotecas (CSV)"
            descricao={descricaoDaPlanilha(relatorio.achados.length)}
            aoEscolher={() => baixar(planilhaDeFalhas(relatorio))}
          />
          <OpcaoDeBaixar
            titulo="Relatório completo (HTML)"
            descricao="Um arquivo só, com todas as abas: abre sozinho no navegador e pode ir por e-mail ou chat. Não leva o login do site."
            aoEscolher={() => baixar(relatorioCompleto(relatorio))}
          />
        </div>
      )}
    </div>
  );
}
