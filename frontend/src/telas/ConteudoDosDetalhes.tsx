import type { Relatorio } from "../relatorio/tiposDoRelatorio.ts";
import type { OrigemDoDado } from "./tiposDaTela.ts";
import ListaAConfirmar from "../zonas/detalhes/ListaAConfirmar.tsx";
import ListaDeBibliotecas from "../zonas/detalhes/ListaDeBibliotecas.tsx";
import ListaDeChecagens from "../zonas/detalhes/ListaDeChecagens.tsx";

interface Props {
  relatorio: Relatorio;
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function ConteudoDosDetalhes({ relatorio, aoVerOrigem }: Props) {
  return (
    <>
      <ListaDeBibliotecas
        bibliotecas={relatorio.bibliotecas}
        achados={relatorio.achados}
        semJavascript={relatorio.analise.limitacoes.some((limitacao) => limitacao.id === "sem_javascript")}
        aoVerOrigem={aoVerOrigem}
      />
      {relatorio.a_confirmar.length > 0 && (
        <ListaAConfirmar bibliotecas={relatorio.a_confirmar} travasAcionadas={relatorio.ia.travas_acionadas} />
      )}
      <ListaDeChecagens
        checagens={relatorio.checagens}
        comFalha={relatorio.resumo.checagens_com_falha}
        naoVerificadas={relatorio.resumo.checagens_nao_verificadas}
      />
    </>
  );
}
