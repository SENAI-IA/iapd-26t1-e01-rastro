import { GRUPOS_DO_PENTEST } from "../conteudo/segurancaAtiva.ts";
import type { ResultadoDoPentest } from "../relatorio/tiposDoRelatorio.ts";
import Icone from "../basicos/Icone.tsx";
import DadosDaExecucao from "./DadosDaExecucao.tsx";
import EscopoDoPentest from "./EscopoDoPentest.tsx";
import GrupoDeValidacoes from "./GrupoDeValidacoes.tsx";
import ResumoDoPentest from "./ResumoDoPentest.tsx";
import { agruparPorCategoria, gruposDoVeredito } from "./agruparValidacoes.ts";
import { comPlural } from "../formatacao/formato.ts";
import "./PainelDaSegurancaAtiva.css";

interface Props {
  pentest: ResultadoDoPentest;
}

export default function PainelDaSegurancaAtiva({ pentest }: Props) {
  const agrupadas = agruparPorCategoria(pentest.validacoes);
  const gruposComItens = GRUPOS_DO_PENTEST.map((grupo) => ({ grupo, itens: gruposDoVeredito(agrupadas, grupo.veredito) })).filter(
    ({ itens }) => itens.length > 0,
  );
  return (
    <section className="painel-da-seguranca-ativa" aria-labelledby="painel-da-seguranca-ativa-titulo">
      <header className="painel-da-seguranca-ativa__cabecalho">
        <span className="painel-da-seguranca-ativa__icone">
          <Icone nome="lupa" tamanho={24} />
        </span>
        <div>
          <span className="painel-da-seguranca-ativa__rotulo">Opcional · com sua autorização</span>
          <h1 id="painel-da-seguranca-ativa-titulo">Segurança ativa</h1>
          <p>
            Com a sua autorização, o Rastro pediu algumas páginas ao site e conferiu as proteções que vieram na resposta.
            Nenhum ataque foi feito, e nada aqui muda a nota.
          </p>
        </div>
      </header>
      <DadosDaExecucao pentest={pentest} />
      <ResumoDoPentest agrupadas={agrupadas} />
      <EscopoDoPentest />
      <div className="painel-da-seguranca-ativa__listas">
        {gruposComItens.map(({ grupo, itens }) => (
          <GrupoDeValidacoes key={grupo.veredito} grupo={grupo} itens={itens} />
        ))}
      </div>
      <p className="painel-da-seguranca-ativa__rodape">
        {comPlural(pentest.validacoes.length, "resultado", "resultados")} no arquivo <code>pentest.json</code>. &ldquo;Corrigir&rdquo; indica
        uma proteção ausente, não um ataque que funcionou.
      </p>
    </section>
  );
}
