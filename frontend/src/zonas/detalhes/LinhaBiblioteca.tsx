import type { Achado, Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";
import AlertasDaBiblioteca from "./AlertasDaBiblioteca.tsx";
import Evidencias from "./Evidencias.tsx";
import ExplicacaoIA from "./ExplicacaoIA.tsx";
import Icone from "../../basicos/Icone.tsx";
import ListaFalhas from "./ListaFalhas.tsx";
import type { OrigemDoDado } from "../../telas/tiposDaTela.ts";
import ResumoDoRisco from "./ResumoDoRisco.tsx";
import Selo from "../../basicos/Selo.tsx";
import SeloDoMetodo from "../../basicos/SeloDoMetodo.tsx";
import { idDaLinhaDaBiblioteca } from "../../calculosDeTela/identificadores.ts";
import "./LinhaBiblioteca.css";

interface Props {
  biblioteca: Biblioteca;
  achados: Achado[];
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function LinhaBiblioteca({ biblioteca, achados, aoVerOrigem }: Props) {
  return (
    <li className="linha-biblioteca" id={idDaLinhaDaBiblioteca(biblioteca.id)}>
      <details>
        <summary className="linha-biblioteca__resumo">
          <span className="linha-biblioteca__seta">
            <Icone nome="seta" />
          </span>
          <span className="linha-biblioteca__nome">
            <b>{biblioteca.pacote}</b> <code>{biblioteca.versao}</code>
          </span>
          <span className="linha-biblioteca__selos">
            <SeloDoMetodo metodo={biblioteca.metodo} />
            {biblioteca.conferida_no_npm === null && (
              <Selo tom="neutro" icone="pacote">
                Não conferida no npm
              </Selo>
            )}
          </span>
          <span className="linha-biblioteca__risco">
            <ResumoDoRisco biblioteca={biblioteca} achados={achados} />
          </span>
        </summary>
        <div className="linha-biblioteca__corpo">
          <button type="button" className="linha-biblioteca__origem" onClick={() => aoVerOrigem({ biblioteca, achados })}>
            <Icone nome="lupa" />
            Ver a origem: HAR, identificação, aviso e nota
          </button>
          <AlertasDaBiblioteca biblioteca={biblioteca} />
          {biblioteca.explicacao && <ExplicacaoIA explicacao={biblioteca.explicacao} />}
          <Evidencias evidencias={biblioteca.evidencias} />
          {biblioteca.motivo_nao_consultada === null && (
            <ListaFalhas achados={achados} aoVerOrigem={(achado) => aoVerOrigem({ biblioteca, achados: [achado] })} />
          )}
        </div>
      </details>
    </li>
  );
}
