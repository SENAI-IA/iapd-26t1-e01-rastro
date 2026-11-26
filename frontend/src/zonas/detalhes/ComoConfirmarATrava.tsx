import type { ReactNode } from "react";
import type { Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";

interface Props {
  trava: string;
  biblioteca: Biblioteca;
}

interface DadosDaConferencia {
  pacote: string;
  versao: string;
  arquivo: ReactNode;
}

const COMO_CONFIRMAR_PELA_TRAVA: Partial<Record<string, (dados: DadosDaConferencia) => ReactNode>> = {
  "pacote existe": ({ pacote, versao }) => (
    <>
      Abra{" "}
      <a href={`https://www.npmjs.com/package/${pacote}?activeTab=versions`} target="_blank" rel="noopener noreferrer">
        {pacote} no npm
      </a>{" "}
      e procure a versão <code>{versao}</code>. Se ela não estiver lá, confira no site do projeto se a versão
      existe e de onde o site a tirou.
    </>
  ),
  "trecho real": ({ arquivo }) => (
    <>Abra {arquivo} no HAR e procure o trecho que a IA citou. Se ele não estiver lá, a evidência foi inventada.</>
  ),
  ancoragem: ({ pacote, versao, arquivo }) => (
    <>
      Procure <code>{versao}</code> no arquivo {arquivo} do HAR, perto do nome <code>{pacote}</code>.
    </>
  ),
  "código confere": ({ pacote, versao, arquivo }) => (
    <>
      Baixe{" "}
      <code>
        {pacote}@{versao}
      </code>{" "}
      do npm e procure, no código publicado, o trecho encontrado em {arquivo}.
    </>
  ),
};

function comoConfirmarQualquerTrava({ versao, arquivo }: DadosDaConferencia): ReactNode {
  return (
    <>
      Procure <code>{versao}</code> no arquivo {arquivo} do HAR e confira o nome e a versão no npm.
    </>
  );
}

export default function ComoConfirmarATrava({ trava, biblioteca }: Props) {
  const { pacote, versao } = biblioteca;
  const arquivo = <code>{biblioteca.evidencias[0]?.url ?? "o script"}</code>;
  const comoConfirmar = COMO_CONFIRMAR_PELA_TRAVA[trava] ?? comoConfirmarQualquerTrava;
  return comoConfirmar({ pacote, versao, arquivo });
}
