import { glossario, type NomeDoTermo } from "../conteudo/glossario.ts";

interface Props {
  termos: NomeDoTermo[];
}

export default function TermosDoPasso({ termos }: Props) {
  return (
    <dl className="tour__termos">
      <span className="tour__rotulo">No glossário</span>
      {termos.map((termo) => (
        <div key={termo}>
          <dt>{termo}</dt>
          <dd>{glossario[termo]}</dd>
        </div>
      ))}
    </dl>
  );
}
