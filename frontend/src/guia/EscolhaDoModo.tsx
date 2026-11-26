import { MODOS_DE_USO, type ModoDeUso } from "../conteudo/guia.ts";
import AnimacaoDoModo from "./AnimacaoDoModo.tsx";

interface Props {
  modo: ModoDeUso;
  aoEscolher: (modo: ModoDeUso) => void;
}

export default function EscolhaDoModo({ modo, aoEscolher }: Props) {
  return (
    <fieldset className="guia-como-usar__modos">
      <legend>Como você quer gravar a visita ao site?</legend>
      {MODOS_DE_USO.map((opcao) => (
        <label key={opcao.modo} className={opcao.modo === modo ? "guia-como-usar__modo guia-como-usar__modo--escolhido" : "guia-como-usar__modo"}>
          <input
            type="radio"
            name="modo-do-guia"
            value={opcao.modo}
            checked={opcao.modo === modo}
            onChange={() => aoEscolher(opcao.modo)}
          />
          <AnimacaoDoModo modo={opcao.modo} />
          <span className="guia-como-usar__modo-titulo">{opcao.titulo}</span>
          <span className="guia-como-usar__modo-resumo">{opcao.resumo}</span>
        </label>
      ))}
    </fieldset>
  );
}
