import NumeroQuePulsa from "./NumeroQuePulsa.tsx";

interface Props {
  arquivos: number;
  totalDeArquivos: number;
  falhas: number;
  totalDeFalhas: number;
}

export default function ContagemDoReplay({ arquivos, totalDeArquivos, falhas, totalDeFalhas }: Props) {
  return (
    <dl className="replay__contagem">
      <div>
        <dt>Arquivos</dt>
        <dd>
          {arquivos}
          <span>/{totalDeArquivos}</span>
        </dd>
      </div>
      <div>
        <dt>Com falha</dt>
        <NumeroQuePulsa valor={falhas} total={totalDeFalhas} />
      </div>
    </dl>
  );
}
