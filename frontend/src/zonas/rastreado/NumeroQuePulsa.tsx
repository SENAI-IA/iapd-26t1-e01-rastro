interface Props {
  valor: number;
  total: number;
}

export default function NumeroQuePulsa({ valor, total }: Props) {
  return (
    <dd key={valor} className={valor > 0 ? "replay__contagem--alerta" : ""}>
      {valor}
      <span>/{total}</span>
    </dd>
  );
}
