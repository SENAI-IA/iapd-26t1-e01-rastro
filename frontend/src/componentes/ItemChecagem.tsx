import type { Checagem, Severidade, SituacaoDaChecagem } from "../tipos.ts";
import Icone, { type NomeDoIcone } from "./Icone.tsx";
import Selo, { type TomDoSelo } from "./Selo.tsx";
import "./ItemChecagem.css";

interface Aparencia {
  rotulo: string;
  tom: TomDoSelo;
  icone: NomeDoIcone;
}

const APARENCIA: Record<SituacaoDaChecagem, Aparencia> = {
  falhou: { rotulo: "Falhou", tom: "critico", icone: "erro" },
  passou: { rotulo: "Passou", tom: "bom", icone: "certo" },
  nao_verificada: { rotulo: "Não verificada", tom: "neutro", icone: "interrogacao" },
};

const ROTULO_DA_SEVERIDADE: Record<Severidade, string> = {
  alta: "alta",
  media: "média",
  baixa: "baixa",
};

interface Props {
  checagem: Checagem;
}

export default function ItemChecagem({ checagem }: Props) {
  const { rotulo, tom, icone } = APARENCIA[checagem.situacao];
  return (
    <li className={`item-checagem item-checagem--${checagem.situacao}`}>
      <details>
        <summary className="item-checagem__resumo">
          <span className="item-checagem__seta">
            <Icone nome="seta" />
          </span>
          <Selo tom={tom} icone={icone}>
            {rotulo}
          </Selo>
          <span className="item-checagem__titulo">
            <code>{checagem.id}</code> {checagem.titulo}
          </span>
          <span className="item-checagem__meta">
            Severidade {ROTULO_DA_SEVERIDADE[checagem.severidade]}
          </span>
        </summary>
        <div className="item-checagem__corpo">
          <p>{checagem.detalhe}</p>
          <p className="item-checagem__quem">
            <Icone nome="pessoa" tamanho={12} />
            Quem resolve: {checagem.quem_resolve}
          </p>
          {checagem.evidencia !== null && (
            <p className="item-checagem__evidencia">
              Evidência: <code>{checagem.evidencia.url}</code>
              {checagem.evidencia.trecho !== null && (
                <>
                  {" "}
                  · <code>{checagem.evidencia.trecho}</code>
                </>
              )}
            </p>
          )}
        </div>
      </details>
    </li>
  );
}
