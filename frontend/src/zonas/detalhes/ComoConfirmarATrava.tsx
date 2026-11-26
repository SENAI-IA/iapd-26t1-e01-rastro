import type { Biblioteca } from "../../relatorio/tiposDoRelatorio.ts";

interface Props {
  trava: string;
  biblioteca: Biblioteca;
}

export default function ComoConfirmarATrava({ trava, biblioteca }: Props) {
  const { pacote, versao } = biblioteca;
  const arquivo = <code>{biblioteca.evidencias[0]?.url ?? "o script"}</code>;
  switch (trava) {
    case "pacote existe":
      return (
        <>
          Abra{" "}
          <a href={`https://www.npmjs.com/package/${pacote}?activeTab=versions`} target="_blank" rel="noopener noreferrer">
            {pacote} no npm
          </a>{" "}
          e procure a versão <code>{versao}</code>. Se ela não estiver lá, confira no site do projeto se a versão
          existe e de onde o site a tirou.
        </>
      );
    case "trecho real":
      return <>Abra {arquivo} no HAR e procure o trecho que a IA citou. Se ele não estiver lá, a evidência foi inventada.</>;
    case "ancoragem":
      return (
        <>
          Procure <code>{versao}</code> no arquivo {arquivo} do HAR, perto do nome <code>{pacote}</code>.
        </>
      );
    case "código confere":
      return (
        <>
          Baixe{" "}
          <code>
            {pacote}@{versao}
          </code>{" "}
          do npm e procure, no código publicado, o trecho encontrado em {arquivo}.
        </>
      );
    default:
      return (
        <>
          Procure <code>{versao}</code> no arquivo {arquivo} do HAR e confira o nome e a versão no npm.
        </>
      );
  }
}
