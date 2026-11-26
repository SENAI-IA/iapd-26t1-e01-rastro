import type { Biblioteca } from "../relatorio/tiposDoRelatorio.ts";
import EtapaDaOrigem from "./EtapaDaOrigem.tsx";
import SeloDoMetodo from "../basicos/SeloDoMetodo.tsx";
import Termo from "../basicos/Termo.tsx";
import { semRepetir } from "../calculosDeTela/semRepetir.ts";
import { textoDoNpm } from "../formatacao/formato.ts";

interface Props {
  biblioteca: Biblioteca;
}

function trechosSemRepeticao(biblioteca: Biblioteca): string[] {
  const trechos = biblioteca.evidencias.map((evidencia) => evidencia.trecho);
  return semRepetir(trechos.filter((trecho) => trecho !== null));
}

export default function EtapaDaIdentificacao({ biblioteca }: Props) {
  return (
    <EtapaDaOrigem numero={2} titulo="Identificação da biblioteca">
      <dl className="painel-origem-do-dado__dados">
        <dt>Método</dt>
        <dd>
          <SeloDoMetodo metodo={biblioteca.metodo} />
        </dd>
        <dt>Resultado</dt>
        <dd>
          <code>
            {biblioteca.pacote}@{biblioteca.versao}
          </code>
        </dd>
        <dt>
          Registro do <Termo nome="npm" />
        </dt>
        <dd>{textoDoNpm(biblioteca.conferida_no_npm)}</dd>
      </dl>
      {trechosSemRepeticao(biblioteca).map((trecho) => (
        <pre key={trecho} className="painel-origem-do-dado__trecho">
          {trecho}
        </pre>
      ))}
    </EtapaDaOrigem>
  );
}
