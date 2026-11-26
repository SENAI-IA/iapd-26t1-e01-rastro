import { DESCRICAO_DA_VALIDACAO } from "../conteudo/segurancaAtiva.ts";
import type { SituacaoDoPentest } from "../relatorio/tiposDoRelatorio.ts";
import Icone, { type NomeDoIcone } from "../basicos/Icone.tsx";
import Selo, { type TomDoSelo } from "../basicos/Selo.tsx";
import Termo from "../basicos/Termo.tsx";
import ListaDeEnderecos from "./ListaDeEnderecos.tsx";
import { contarEnderecos, type ValidacaoAgrupada, type Veredito } from "./agruparValidacoes.ts";
import { semRepetir } from "../calculosDeTela/semRepetir.ts";
import { comPlural } from "../formatacao/formato.ts";
import "./ItemDaSegurancaAtiva.css";

interface Aparencia {
  rotulo: string;
  tom: TomDoSelo;
  icone: NomeDoIcone;
}

const APARENCIA_DO_VEREDITO: Record<Veredito, Aparencia> = {
  corrigir: { rotulo: "Corrigir", tom: "critico", icone: "erro" },
  em_ordem: { rotulo: "Em ordem", tom: "bom", icone: "certo" },
  sem_resposta: { rotulo: "Não conferido", tom: "neutro", icone: "interrogacao" },
};

const SITUACAO_DO_VEREDITO: Record<Veredito, SituacaoDoPentest> = {
  corrigir: "falhou",
  em_ordem: "passou",
  sem_resposta: "nao_verificada",
};

function textoDaContagem(grupo: ValidacaoAgrupada): string {
  const { total, comFalha } = contarEnderecos(grupo);
  if (grupo.veredito === "corrigir") {
    return `em ${comFalha} de ${comPlural(total, "endereço", "endereços")}`;
  }
  return comPlural(total, "endereço", "endereços");
}

function detalhesQueExplicam(grupo: ValidacaoAgrupada): string[] {
  const situacaoQueExplica = SITUACAO_DO_VEREDITO[grupo.veredito];
  const queExplicam = grupo.validacoes.filter((validacao) => validacao.situacao === situacaoQueExplica);
  return semRepetir(queExplicam.map((validacao) => validacao.detalhe));
}

interface Props {
  grupo: ValidacaoAgrupada;
}

export default function ItemDaSegurancaAtiva({ grupo }: Props) {
  const descricao = DESCRICAO_DA_VALIDACAO[grupo.categoria];
  const aparencia = APARENCIA_DO_VEREDITO[grupo.veredito];
  const referencia = grupo.validacoes[0]?.referencia ?? null;
  return (
    <li className={`item-da-seguranca-ativa item-da-seguranca-ativa--${grupo.veredito}`}>
      <details>
        <summary className="item-da-seguranca-ativa__resumo">
          <span className="item-da-seguranca-ativa__seta"><Icone nome="seta" /></span>
          <Selo tom={aparencia.tom} icone={aparencia.icone}>{aparencia.rotulo}</Selo>
          <span className="item-da-seguranca-ativa__titulo">{descricao.nome}</span>
          <span className="item-da-seguranca-ativa__contagem">{textoDaContagem(grupo)}</span>
        </summary>
        <div className="item-da-seguranca-ativa__corpo">
          <p className="item-da-seguranca-ativa__porque">{descricao.porque}</p>
          <div>
            <h3>O que o Rastro viu</h3>
            <ul className="item-da-seguranca-ativa__detalhes">
              {detalhesQueExplicam(grupo).map((detalhe) => <li key={detalhe}>{detalhe}</li>)}
            </ul>
          </div>
          <ListaDeEnderecos validacoes={grupo.validacoes} />
          {referencia && (
            <p className="item-da-seguranca-ativa__referencia">
              Teste do guia <Termo nome="WSTG" />: <code>{referencia}</code>
            </p>
          )}
        </div>
      </details>
    </li>
  );
}
