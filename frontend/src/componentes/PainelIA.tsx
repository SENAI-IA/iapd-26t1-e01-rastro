import type { DadosDaIA } from "../tipos.ts";
import ChamadaDaIA from "./ChamadaDaIA.tsx";
import Icone from "./Icone.tsx";
import Selo from "./Selo.tsx";
import { formatarTokens, plural } from "./formato.ts";
import Termo from "./Termo.tsx";
import "./PainelIA.css";

interface Props {
  ia: DadosDaIA;
  provedor: string | null;
}

export default function PainelIA({ ia, provedor }: Props) {
  const comparacao = ia.com_e_sem_ia;
  return (
    <section className="painel-ia" aria-labelledby="painel-ia-titulo">
      <div className="painel-ia__cabecalho">
        <h2 id="painel-ia-titulo">
          <Selo tom="ia" icone="ia">
            IA
          </Selo>
          Onde a IA entrou nesta análise
        </h2>
        <p>A IA sugere, a regra confirma. A nota de risco e a prioridade vêm sempre da fórmula.</p>
      </div>

      {provedor === null ? (
        <p className="painel-ia__desligada">
          <Icone nome="info" />
          <span>
            <b>IA desligada nesta análise.</b> Nenhuma chamada foi feita. As travas que conferem o registro do{" "}
            <Termo nome="npm" /> e a faixa de versão afetada rodam também sem IA.
          </span>
        </p>
      ) : (
        <>
          {comparacao && (
            <div className="painel-ia__tabela">
              <table>
                <thead>
                  <tr>
                    <th scope="col">
                      <span className="painel-ia__oculto">Medida</span>
                    </th>
                    <th scope="col">
                      Só por <Termo nome="Assinatura">assinatura</Termo>
                    </th>
                    <th scope="col">Com a IA</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="row">Bibliotecas confirmadas</th>
                    <td>{comparacao.bibliotecas.so_por_assinatura}</td>
                    <td>{comparacao.bibliotecas.com_ia}</td>
                  </tr>
                  <tr>
                    <th scope="row">Falhas encontradas</th>
                    <td>{comparacao.achados.so_por_assinatura}</td>
                    <td>{comparacao.achados.com_ia}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          <div className="painel-ia__bloco">
            <h3>O que a IA recebeu e devolveu</h3>
            <p>
              Provedor <code>{provedor}</code>: {plural(ia.chamadas.length, "chamada", "chamadas")}, total de{" "}
              <Termo nome="Token">tokens</Termo>: {formatarTokens(ia.tokens_total)}. A IA recebe só trechos
              escolhidos pelo Rastro, sem cookies, senhas ou tokens de sessão.
            </p>
            {ia.chamadas.length === 0 ? (
              <p className="painel-ia__vazio">Nenhuma chamada à IA: não havia achado para explicar.</p>
            ) : (
              <ol className="painel-ia__lista">
                {ia.chamadas.map((chamada, indice) => (
                  <ChamadaDaIA key={indice} chamada={chamada} />
                ))}
              </ol>
            )}
          </div>
        </>
      )}

      <div className="painel-ia__bloco">
        <h3>
          <Termo nome="Trava">Travas</Termo> acionadas
        </h3>
        {ia.travas_acionadas.length === 0 ? (
          <p className="painel-ia__vazio">Nenhuma trava precisou barrar nada nesta análise.</p>
        ) : (
          <ul className="painel-ia__lista">
            {ia.travas_acionadas.map((trava, indice) => (
              <li key={indice} className="painel-ia__trava">
                <Selo tom="serio" icone="triangulo">
                  Trava "{trava.trava}"
                </Selo>
                <span>
                  <b>Barrou:</b> {trava.alvo}
                </span>
                <span>
                  <b>Por quê:</b> {trava.motivo}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
