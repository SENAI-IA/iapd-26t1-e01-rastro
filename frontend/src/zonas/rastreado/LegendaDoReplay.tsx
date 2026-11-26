const ITENS_DA_LEGENDA = [
  { simbolo: "requisicao", texto: "arquivo recebido" },
  { simbolo: "falha", texto: "trouxe biblioteca com falha" },
  { simbolo: "anel", texto: "anel: tipo de arquivo" },
  { simbolo: "giro", texto: "giro: ordem de chegada" },
];

export default function LegendaDoReplay() {
  return (
    <ul className="replay__legenda" aria-label="Legenda">
      {ITENS_DA_LEGENDA.map((item) => (
        <li key={item.simbolo}>
          <span className={`replay__simbolo replay__simbolo--${item.simbolo}`} aria-hidden="true" />
          {item.texto}
        </li>
      ))}
    </ul>
  );
}
