const ESPACO_ENTRE_LINHAS = 14;

interface Props {
  primeiraLinha: number;
  comprimentos: number[];
}

export default function LinhasQueAparecem({ primeiraLinha, comprimentos }: Props) {
  return (
    <>
      {comprimentos.map((fim, posicao) => {
        const y = primeiraLinha + posicao * ESPACO_ENTRE_LINHAS;
        return <line key={y} className="ilustracao-do-guia__linha" pathLength="1" x1="22" y1={y} x2={fim} y2={y} />;
      })}
    </>
  );
}
