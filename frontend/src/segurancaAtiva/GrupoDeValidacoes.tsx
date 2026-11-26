import type { GrupoDoPentest } from "../conteudo/segurancaAtiva.ts";
import type { ValidacaoAgrupada } from "./agruparValidacoes.ts";
import ItemDoPentest from "./ItemDoPentest.tsx";
import { plural } from "../formatacao/formato.ts";

interface Props {
  grupo: GrupoDoPentest;
  itens: ValidacaoAgrupada[];
}

export default function GrupoDeValidacoes({ grupo, itens }: Props) {
  return (
    <section className="painel-pentest__grupo" aria-labelledby={`pentest-${grupo.veredito}`}>
      <div>
        <h2 id={`pentest-${grupo.veredito}`}>{grupo.titulo}</h2>
        <p>{plural(itens.length, "proteção", "proteções")}: {grupo.legenda}.</p>
      </div>
      <ul>
        {itens.map((item) => (
          <ItemDoPentest key={item.categoria} grupo={item} />
        ))}
      </ul>
    </section>
  );
}
