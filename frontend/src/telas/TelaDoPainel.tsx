import type { ReactNode } from "react";
import type { Acao, Relatorio } from "../relatorio/tiposDoRelatorio.ts";
import type { OrigemDoDado } from "./tiposDaTela.ts";
import { ZONAS, type NomeDaZona } from "../conteudo/zonas.ts";
import CabecalhoAnalise from "../moldura/CabecalhoAnalise.tsx";
import Indicadores from "../zonas/rastreado/Indicadores.tsx";
import ConteudoDosDetalhes from "./ConteudoDosDetalhes.tsx";
import PainelIA from "../zonas/rastreado/PainelIA.tsx";
import PlanoDeAcao from "../zonas/agir/PlanoDeAcao.tsx";
import ReplayDaVisita from "../zonas/rastreado/ReplayDaVisita.tsx";
import Zona from "../moldura/Zona.tsx";

interface Props {
  relatorio: Relatorio;
  zonaEmFoco: NomeDaZona | null;
  aoFocar: (zona: NomeDaZona) => void;
  aoIrParaBiblioteca: (id: string) => void;
  aoAbrirTask: (acao: Acao) => void;
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function TelaDoPainel({
  relatorio,
  zonaEmFoco,
  aoFocar,
  aoIrParaBiblioteca,
  aoAbrirTask,
  aoVerOrigem,
}: Props) {
  const zonasVisiveis = zonaEmFoco === null ? ZONAS : ZONAS.filter((zona) => zona.id === zonaEmFoco);

  const conteudoDaZona = (zona: NomeDaZona): ReactNode => {
    switch (zona) {
      case "rastreado":
        return (
          <>
            {relatorio.visita && relatorio.visita.length > 0 && (
              <ReplayDaVisita
                passos={relatorio.visita}
                bibliotecas={relatorio.bibliotecas}
                aoIrParaBiblioteca={aoIrParaBiblioteca}
              />
            )}
            <Indicadores resumo={relatorio.resumo} primeiraAcao={relatorio.plano_de_acao[0]} />
            <PainelIA ia={relatorio.ia} provedor={relatorio.analise.ia} />
          </>
        );
      case "agir":
        return <PlanoDeAcao acoes={relatorio.plano_de_acao} aoAbrirTask={aoAbrirTask} />;
      case "detalhes":
        return <ConteudoDosDetalhes relatorio={relatorio} aoVerOrigem={aoVerOrigem} />;
    }
  };

  return (
    <>
      {zonaEmFoco === null && <CabecalhoAnalise analise={relatorio.analise} />}
      {zonasVisiveis.map((zona) => (
        <Zona key={zona.id} zona={zona} aoFocar={zonaEmFoco ? undefined : () => aoFocar(zona.id)}>
          {conteudoDaZona(zona.id)}
        </Zona>
      ))}
    </>
  );
}
