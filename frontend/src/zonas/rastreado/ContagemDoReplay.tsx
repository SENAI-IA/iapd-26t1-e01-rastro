import NumeroQuePulsa from "./NumeroQuePulsa.tsx";

interface Props {
  arquivos: number;
  totalDeArquivos: number;
  falhas: number;
}

export default function ContagemDoReplay({ arquivos, totalDeArquivos, falhas }: Props) {
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
        <NumeroQuePulsa valor={falhas} />
      </div>
    </dl>
  );
}
