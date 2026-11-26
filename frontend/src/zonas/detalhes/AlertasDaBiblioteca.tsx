import type { Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";
import Icone from "../../basicos/Icone.tsx";
import Termo from "../../basicos/Termo.tsx";

interface Props {
  biblioteca: Biblioteca;
}

export default function AlertasDaBiblioteca({ biblioteca }: Props) {
  return (
    <>
      {biblioteca.motivo_nao_consultada !== null && (
        <p className="linha-biblioteca__alerta">
          <Icone nome="triangulo" />
          <span>
            Não consultada no GitHub Advisory: {biblioteca.motivo_nao_consultada}. As falhas desta
            biblioteca podem não aparecer aqui; rode a análise de novo com rede.
          </span>
        </p>
      )}
      {biblioteca.conferida_no_npm === null && (
        <p className="linha-biblioteca__alerta">
          <Icone nome="pacote" />
          <span>
            O registro do <Termo nome="npm" /> não respondeu, então não deu para conferir que{" "}
            <code>
              {biblioteca.pacote}@{biblioteca.versao}
            </code>{" "}
            foi publicado. A identificação vem da <Termo nome="Assinatura">assinatura</Termo>.
          </span>
        </p>
      )}
    </>
  );
}
