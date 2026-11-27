interface Props {
  titulo: string;
  descricao: string;
  aoEscolher: () => void;
}

export default function OpcaoDeBaixar({ titulo, descricao, aoEscolher }: Props) {
  return (
    <button type="button" className="menu-de-baixar__opcao" onClick={aoEscolher}>
      <span className="menu-de-baixar__titulo">{titulo}</span>
      <span className="menu-de-baixar__descricao">{descricao}</span>
    </button>
  );
}
