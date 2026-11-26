import type { Checagem, Severidade, SituacaoDaChecagem } from "../../relatorio/tiposDoRelatorio.ts";
import Icone, { type NomeDoIcone } from "../../basicos/Icone.tsx";
import Selo, { type TomDoSelo } from "../../basicos/Selo.tsx";
import "./ItemDaChecagem.css";

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

export default function ItemDaChecagem({ checagem }: Props) {
  const { rotulo, tom, icone } = APARENCIA[checagem.situacao];
  return (
    <li className={`item-da-checagem item-da-checagem--${checagem.situacao}`}>
      <details>
        <summary className="item-da-checagem__resumo">
          <span className="item-da-checagem__seta">
            <Icone nome="seta" />
          </span>
          <Selo tom={tom} icone={icone}>
            {rotulo}
          </Selo>
          <span className="item-da-checagem__titulo">
            <code>{checagem.id}</code> {checagem.titulo}
          </span>
          <span className="item-da-checagem__detalhes">
            Severidade {ROTULO_DA_SEVERIDADE[checagem.severidade]}
          </span>
        </summary>
        <div className="item-da-checagem__corpo">
          <p>{checagem.detalhe}</p>
          <p className="item-da-checagem__quem">
            <Icone nome="pessoa" tamanho={12} />
            Quem resolve: {checagem.quem_resolve}
          </p>
          {checagem.evidencia !== null && (
            <p className="item-da-checagem__evidencia">
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
