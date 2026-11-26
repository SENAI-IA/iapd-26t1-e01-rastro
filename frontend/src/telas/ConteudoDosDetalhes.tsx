import type { Relatorio } from "../relatorio/tiposDoRelatorio.ts";
import type { OrigemDoDado } from "./tiposDaTela.ts";
import ListaAConfirmar from "../zonas/detalhes/ListaAConfirmar.tsx";
import ListaBibliotecas from "../zonas/detalhes/ListaBibliotecas.tsx";
import ListaChecagens from "../zonas/detalhes/ListaChecagens.tsx";

interface Props {
  relatorio: Relatorio;
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function ConteudoDosDetalhes({ relatorio, aoVerOrigem }: Props) {
  return (
    <>
      <ListaBibliotecas
        bibliotecas={relatorio.bibliotecas}
        achados={relatorio.achados}
        semJavascript={relatorio.analise.limitacoes.some((limitacao) => limitacao.id === "sem_javascript")}
        aoVerOrigem={aoVerOrigem}
      />
      {relatorio.a_confirmar.length > 0 && (
        <ListaAConfirmar bibliotecas={relatorio.a_confirmar} travasAcionadas={relatorio.ia.travas_acionadas} />
      )}
      <ListaChecagens
        checagens={relatorio.checagens}
        comFalha={relatorio.resumo.checagens_com_falha}
        naoVerificadas={relatorio.resumo.checagens_nao_verificadas}
      />
    </>
  );
}
