interface Props {
  valor: number;
}

export default function NumeroQuePulsa({ valor }: Props) {
  return (
    <dd key={valor} className={valor > 0 ? "replay__contagem--alerta" : ""}>
      {valor}
    </dd>
  );
}
