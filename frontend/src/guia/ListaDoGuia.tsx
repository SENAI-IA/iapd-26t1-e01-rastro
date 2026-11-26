import type { ItemDoGuia } from "../conteudo/guia.ts";
import TextoComMarcas from "../basicos/TextoComMarcas.tsx";

interface Props {
  itens: ItemDoGuia[];
}

export default function ListaDoGuia({ itens }: Props) {
  return (
    <ul>
      {itens.map((item) => (
        <li key={item.texto}>
          <TextoComMarcas texto={item.texto} />
        </li>
      ))}
    </ul>
  );
}
