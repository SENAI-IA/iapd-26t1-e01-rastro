import type { GrupoDoPentest } from "../conteudo/segurancaAtiva.ts";
import type { ValidacaoAgrupada } from "./agruparValidacoes.ts";
import ItemDaSegurancaAtiva from "./ItemDaSegurancaAtiva.tsx";
import { comPlural } from "../formatacao/formato.ts";

interface Props {
  grupo: GrupoDoPentest;
  itens: ValidacaoAgrupada[];
}

export default function GrupoDeValidacoes({ grupo, itens }: Props) {
  return (
    <section className="painel-da-seguranca-ativa__grupo" aria-labelledby={`pentest-${grupo.veredito}`}>
      <div>
        <h2 id={`pentest-${grupo.veredito}`}>{grupo.titulo}</h2>
        <p>{comPlural(itens.length, "proteção", "proteções")}: {grupo.legenda}.</p>
      </div>
      <ul>
        {itens.map((item) => (
          <ItemDaSegurancaAtiva key={item.categoria} grupo={item} />
        ))}
      </ul>
    </section>
  );
}
