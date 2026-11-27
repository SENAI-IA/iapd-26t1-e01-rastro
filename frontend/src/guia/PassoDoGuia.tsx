import type { DescricaoDoPasso } from "../conteudo/guia.ts";
import ComandosDoPasso from "./ComandosDoPasso.tsx";
import Icone from "../basicos/Icone.tsx";
import IlustracaoDoGuia from "./IlustracaoDoGuia.tsx";
import TerminalDoPasso from "./TerminalDoPasso.tsx";
import { ehTerminalDoGuia } from "../conteudo/simulacoesDoGuia.ts";
import TextoComMarcas from "../basicos/TextoComMarcas.tsx";
import { idDoPassoDoGuia } from "../calculosDeTela/identificadores.ts";
import "./PassoDoGuia.css";

interface Props {
  numero: number;
  passo: DescricaoDoPasso;
  feito: boolean;
  aoMarcar: () => void;
  simulando: boolean;
  aoSimular: () => void;
  aoFecharSimulacao: () => void;
}

export default function PassoDoGuia({ numero, passo, feito, aoMarcar, simulando, aoSimular, aoFecharSimulacao }: Props) {
  return (
    <li
      id={idDoPassoDoGuia(numero)}
      tabIndex={-1}
      className={feito ? "passo-do-guia passo-do-guia--feito" : "passo-do-guia"}
    >
      <div className="passo-do-guia__numero" aria-hidden="true">
        {feito ? <Icone nome="certo" tamanho={18} /> : numero}
      </div>
      <div className="passo-do-guia__texto">
        <h2>
          <span className="passo-do-guia__leitor">Passo {numero}: </span>
          {passo.titulo}
        </h2>
        <p>
          <TextoComMarcas texto={passo.texto} />
        </p>
        {passo.comandos && <ComandosDoPasso comandos={passo.comandos} />}
        {passo.observacao && (
          <p className="passo-do-guia__observacao">
            <TextoComMarcas texto={passo.observacao} />
          </p>
        )}
        <button type="button" className="passo-do-guia__marcar" aria-pressed={feito} onClick={aoMarcar}>
          {feito ? "Feito" : "Marcar como feito"}
        </button>
      </div>
      {ehTerminalDoGuia(passo.ilustracao) ? (
        <TerminalDoPasso terminal={passo.ilustracao} simulando={simulando} aoSimular={aoSimular} aoFechar={aoFecharSimulacao} />
      ) : (
        <IlustracaoDoGuia ilustracao={passo.ilustracao} />
      )}
    </li>
  );
}
