import type { ReactNode } from "react";
import type { Acao, Relatorio } from "../relatorio/tiposDoRelatorio.ts";
import type { OrigemDoDado } from "./tiposDaTela.ts";
import { ZONAS, type NomeDaZona } from "../conteudo/zonas.ts";
import CabecalhoDaAnalise from "../moldura/CabecalhoDaAnalise.tsx";
import Indicadores from "../zonas/rastreado/Indicadores.tsx";
import ConteudoDosDetalhes from "./ConteudoDosDetalhes.tsx";
import PainelDaIA from "../zonas/rastreado/PainelDaIA.tsx";
import PlanoDeAcao from "../zonas/agir/PlanoDeAcao.tsx";
import ReplayDaVisita from "../zonas/rastreado/ReplayDaVisita.tsx";
import ZonaDoPainel from "../moldura/ZonaDoPainel.tsx";

interface Props {
  relatorio: Relatorio;
  zonaEmFoco: NomeDaZona | null;
  aoFocar: (zona: NomeDaZona) => void;
  aoIrParaBiblioteca: (id: string) => void;
  aoAbrirTarefa: (acao: Acao) => void;
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function TelaDoPainel({
  relatorio,
  zonaEmFoco,
  aoFocar,
  aoIrParaBiblioteca,
  aoAbrirTarefa,
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
            <PainelDaIA ia={relatorio.ia} provedor={relatorio.analise.ia} />
          </>
        );
      case "agir":
        return <PlanoDeAcao acoes={relatorio.plano_de_acao} aoAbrirTarefa={aoAbrirTarefa} />;
      case "detalhes":
        return <ConteudoDosDetalhes relatorio={relatorio} aoVerOrigem={aoVerOrigem} />;
    }
  };

  return (
    <>
      {zonaEmFoco === null && <CabecalhoDaAnalise analise={relatorio.analise} />}
      {zonasVisiveis.map((zona) => (
        <ZonaDoPainel key={zona.id} zona={zona} aoFocar={zonaEmFoco ? undefined : () => aoFocar(zona.id)}>
          {conteudoDaZona(zona.id)}
        </ZonaDoPainel>
      ))}
    </>
  );
}
