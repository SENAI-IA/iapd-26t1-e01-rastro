import type { Achado, Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";
import AlertasDaBiblioteca from "./AlertasDaBiblioteca.tsx";
import Evidencias from "./Evidencias.tsx";
import ExplicacaoDaIA from "./ExplicacaoDaIA.tsx";
import Icone from "../../basicos/Icone.tsx";
import ListaDeFalhas from "./ListaDeFalhas.tsx";
import type { OrigemDoDado } from "../../telas/tiposDaTela.ts";
import ResumoDoRisco from "./ResumoDoRisco.tsx";
import Selo from "../../basicos/Selo.tsx";
import SeloDoMetodo from "../../basicos/SeloDoMetodo.tsx";
import { idDoItemDaBiblioteca } from "../../calculosDeTela/identificadores.ts";
import "./ItemDaBiblioteca.css";

interface Props {
  biblioteca: Biblioteca;
  achados: Achado[];
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function ItemDaBiblioteca({ biblioteca, achados, aoVerOrigem }: Props) {
  return (
    <li className="item-da-biblioteca" id={idDoItemDaBiblioteca(biblioteca.id)}>
      <details>
        <summary className="item-da-biblioteca__resumo">
          <span className="item-da-biblioteca__seta">
            <Icone nome="seta" />
          </span>
          <span className="item-da-biblioteca__nome">
            <b>{biblioteca.pacote}</b> <code>{biblioteca.versao}</code>
          </span>
          <span className="item-da-biblioteca__selos">
            <SeloDoMetodo metodo={biblioteca.metodo} />
            {biblioteca.conferida_no_npm === null && (
              <Selo tom="neutro" icone="pacote">
                Não conferida no npm
              </Selo>
            )}
          </span>
          <span className="item-da-biblioteca__risco">
            <ResumoDoRisco biblioteca={biblioteca} achados={achados} />
          </span>
        </summary>
        <div className="item-da-biblioteca__corpo">
          <button type="button" className="item-da-biblioteca__origem" onClick={() => aoVerOrigem({ biblioteca, achados })}>
            <Icone nome="lupa" />
            Ver a origem: HAR, identificação, aviso e nota
          </button>
          <AlertasDaBiblioteca biblioteca={biblioteca} />
          {biblioteca.explicacao && <ExplicacaoDaIA explicacao={biblioteca.explicacao} />}
          <Evidencias evidencias={biblioteca.evidencias} />
          {biblioteca.motivo_nao_consultada === null && (
            <ListaDeFalhas achados={achados} aoVerOrigem={(achado) => aoVerOrigem({ biblioteca, achados: [achado] })} />
          )}
        </div>
      </details>
    </li>
  );
}
