import Termo from "../../basicos/Termo.tsx";

interface Props {
  semJavascript: boolean;
}

export default function ListaVazia({ semJavascript }: Props) {
  if (!semJavascript) {
    return <p className="lista-bibliotecas__vazio">Nenhuma biblioteca confirmada nesta gravação.</p>;
  }
  return (
    <p className="lista-bibliotecas__vazio">
      <strong>Nenhuma biblioteca pôde ser analisada:</strong> o <Termo nome="HAR" /> não trouxe nenhum script.
      Grave de novo com o filtro da aba Rede em <strong>Todos</strong> e o cache desativado.
    </p>
  );
}
