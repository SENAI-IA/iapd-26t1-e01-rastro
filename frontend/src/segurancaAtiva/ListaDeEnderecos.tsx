import type { SituacaoDoPentest, ValidacaoDoPentest } from "../relatorio/tiposDoRelatorio.ts";
import Icone, { type NomeDoIcone } from "../basicos/Icone.tsx";
import { escreverStatus, comPlural } from "../formatacao/formato.ts";

const ICONE_DA_SITUACAO: Record<SituacaoDoPentest, NomeDoIcone> = {
  falhou: "erro",
  passou: "certo",
  nao_verificada: "interrogacao",
};

const NOME_DA_SITUACAO: Record<SituacaoDoPentest, string> = {
  falhou: "falhou",
  passou: "passou",
  nao_verificada: "não conferido",
};

interface Props {
  validacoes: ValidacaoDoPentest[];
}

export default function ListaDeEnderecos({ validacoes }: Props) {
  return (
    <details className="item-da-seguranca-ativa__enderecos">
      <summary>Ver {comPlural(validacoes.length, "resultado", "resultados")} por endereço</summary>
      <ul>
        {validacoes.map((validacao) => (
          <li key={validacao.id} className={`item-da-seguranca-ativa__endereco--${validacao.situacao}`}>
            <span role="img" aria-label={NOME_DA_SITUACAO[validacao.situacao]} title={NOME_DA_SITUACAO[validacao.situacao]}>
              <Icone nome={ICONE_DA_SITUACAO[validacao.situacao]} tamanho={13} />
            </span>
            <code>{validacao.requisicao.url}</code>
            <span className="item-da-seguranca-ativa__dados-da-requisicao">
              {validacao.requisicao.metodo} · {escreverStatus(validacao.requisicao.status)} · {validacao.id}
            </span>
          </li>
        ))}
      </ul>
    </details>
  );
}
