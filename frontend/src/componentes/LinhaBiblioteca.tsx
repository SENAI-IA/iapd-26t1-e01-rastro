import type { Achado, Biblioteca } from "../tipos.ts";
import Evidencias from "./Evidencias.tsx";
import ExplicacaoIA from "./ExplicacaoIA.tsx";
import Icone from "./Icone.tsx";
import ListaFalhas from "./ListaFalhas.tsx";
import type { OrigemDoDado } from "./PainelOrigemDoDado.tsx";
import Selo from "./Selo.tsx";
import SeloDePrioridade from "./SeloDePrioridade.tsx";
import SeloDoMetodo from "./SeloDoMetodo.tsx";
import { formatarNota, plural } from "./formato.ts";
import Termo from "./Termo.tsx";
import "./LinhaBiblioteca.css";

interface Props {
  biblioteca: Biblioteca;
  achados: Achado[];
  aoVerOrigem: (origem: OrigemDoDado) => void;
}

export default function LinhaBiblioteca({ biblioteca, achados, aoVerOrigem }: Props) {
  const naoConsultada = biblioteca.motivo_nao_consultada !== null;
  return (
    <li className="linha-biblioteca">
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
            {naoConsultada ? (
              <Selo tom="serio" icone="triangulo">
                Não consultada
              </Selo>
            ) : achados.length === 0 ? (
              <Selo tom="bom" icone="certo">
                Sem falhas conhecidas
              </Selo>
            ) : (
              <>
                <span>{plural(achados.length, "falha", "falhas")}</span>
                <span className="linha-biblioteca__nota">
                  {biblioteca.nota === null ? "Sem nota" : `Nota ${formatarNota(biblioteca.nota)}`}
                </span>
                <SeloDePrioridade prioridade={achados[0].nota.prioridade} />
              </>
            )}
          </span>
        </summary>
        <div className="linha-biblioteca__corpo">
          <button
            type="button"
            className="linha-biblioteca__origem"
            onClick={() => aoVerOrigem({ biblioteca, achados })}
          >
            <Icone nome="lupa" />
            Ver a origem: HAR, identificação, aviso e nota
          </button>
          {naoConsultada && (
            <p className="linha-biblioteca__alerta">
              <Icone nome="triangulo" />
              <span>
                Não consultada no GitHub Advisory: {biblioteca.motivo_nao_consultada}. As falhas desta
                biblioteca podem não aparecer aqui; rode a análise de novo com rede.
              </span>
            </p>
          )}
          {biblioteca.conferida_no_npm === null && (
            <p className="linha-biblioteca__alerta">
              <Icone nome="pacote" />
              <span>
                O registro do <Termo nome="npm" /> não respondeu, então não deu para conferir que{" "}
                <code>
                  {biblioteca.pacote}@{biblioteca.versao}
                </code>{" "}
                foi publicado. A identificação vem da <Termo nome="Assinatura">assinatura</Termo>.
              </span>
            </p>
          )}
          {biblioteca.explicacao && <ExplicacaoIA explicacao={biblioteca.explicacao} />}
          <Evidencias evidencias={biblioteca.evidencias} />
          {!naoConsultada && (
            <ListaFalhas achados={achados} aoVerOrigem={(achado) => aoVerOrigem({ biblioteca, achados: [achado] })} />
          )}
        </div>
      </details>
    </li>
  );
}
