import type { OrigemDoDado } from "../telas/tiposDaTela.ts";
import SeloDePrioridade from "../basicos/SeloDePrioridade.tsx";

interface Props {
  origem: OrigemDoDado;
}

export default function ContasDaNota({ origem }: Props) {
  const { biblioteca, achados } = origem;
  if (achados.length === 0) {
    return (
      <p className="painel-origem__texto">
        {biblioteca.motivo_nao_consultada !== null
          ? "Sem a consulta ao aviso, não há nota."
          : "Sem aviso, não há nota a calcular."}
      </p>
    );
  }
  return (
    <ul className="painel-origem__lista">
      {achados.map(({ aviso, nota }) => (
        <li key={aviso.ghsa} className="painel-origem__conta">
          {achados.length > 1 && <span className="painel-origem__texto">{aviso.ghsa}</span>}
          <code className="painel-origem__formula">{nota.conta}</code>
          <SeloDePrioridade prioridade={nota.prioridade} />
        </li>
      ))}
    </ul>
  );
}
