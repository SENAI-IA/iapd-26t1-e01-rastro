import type { ComESemIA } from "../../relatorio/tiposDoRelatorio.ts";
import Termo from "../../basicos/Termo.tsx";

interface Props {
  comparacao: ComESemIA;
}

export default function ComparacaoComESemIA({ comparacao }: Props) {
  return (
    <div className="painel-da-ia__tabela">
      <table>
        <thead>
          <tr>
            <th scope="col">
              <span className="painel-da-ia__oculto">Medida</span>
            </th>
            <th scope="col">
              Só por <Termo nome="Assinatura">assinatura</Termo>
            </th>
            <th scope="col">Com a IA</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Bibliotecas confirmadas</th>
            <td>{comparacao.bibliotecas.so_por_assinatura}</td>
            <td>{comparacao.bibliotecas.com_ia}</td>
          </tr>
          <tr>
            <th scope="row">Falhas encontradas</th>
            <td>{comparacao.achados.so_por_assinatura}</td>
            <td>{comparacao.achados.com_ia}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
