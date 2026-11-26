import { MODOS_DE_USO, type ModoDeUso } from "../conteudo/guia.ts";
import AnimacaoDoModo from "./AnimacaoDoModo.tsx";

interface Props {
  modo: ModoDeUso;
  aoEscolher: (modo: ModoDeUso) => void;
}

export default function EscolhaDoModo({ modo, aoEscolher }: Props) {
  return (
    <fieldset className="guia__modos">
      <legend>Como você quer gravar a visita ao site?</legend>
      {MODOS_DE_USO.map((opcao) => (
        <label key={opcao.modo} className={opcao.modo === modo ? "guia__modo guia__modo--escolhido" : "guia__modo"}>
          <input
            type="radio"
            name="guia-modo"
            value={opcao.modo}
            checked={opcao.modo === modo}
            onChange={() => aoEscolher(opcao.modo)}
          />
          <AnimacaoDoModo modo={opcao.modo} />
          <span className="guia__modo-titulo">{opcao.titulo}</span>
          <span className="guia__modo-resumo">{opcao.resumo}</span>
        </label>
      ))}
    </fieldset>
  );
}
