import { useEffect, useRef, type MouseEvent } from "react";
import type { Achado, Aviso, Biblioteca, CampoComOrigem } from "../tipos.ts";
import EtapaDaOrigem from "./EtapaDaOrigem.tsx";
import Icone from "./Icone.tsx";
import SeloDePrioridade from "./SeloDePrioridade.tsx";
import SeloDoMetodo from "./SeloDoMetodo.tsx";
import { formatarNota, formatarPercentil } from "./formato.ts";
import Termo from "./Termo.tsx";
import "./PainelOrigemDoDado.css";

export interface OrigemDoDado {
  biblioteca: Biblioteca;
  achados: Achado[];
}

interface Props {
  origem: OrigemDoDado;
  aoFechar: () => void;
}

export default function PainelOrigemDoDado({ origem, aoFechar }: Props) {
  const painel = useRef<HTMLDialogElement>(null);
  const { biblioteca, achados } = origem;
  const naoConsultada = biblioteca.motivo_nao_consultada !== null;

  useEffect(() => {
    painel.current?.showModal();
  }, []);

  const fechar = () => painel.current?.close();
  const fecharAoClicarFora = (evento: MouseEvent<HTMLDialogElement>) => {
    if (evento.target === evento.currentTarget) {
      fechar();
    }
  };

  return (
    <dialog
      ref={painel}
      className="painel-origem"
      aria-labelledby="painel-origem-titulo"
      onClose={aoFechar}
      onClick={fecharAoClicarFora}
    >
      <div className="painel-origem__conteudo">
        <header className="painel-origem__cabecalho">
          <div>
            <span className="painel-origem__rotulo">Origem do dado</span>
            <h2 id="painel-origem-titulo">{tituloDaOrigem(origem)}</h2>
          </div>
          <button type="button" className="painel-origem__fechar" onClick={fechar} aria-label="Fechar a origem do dado">
            <Icone nome="fechar" tamanho={16} />
          </button>
        </header>

        <div className="painel-origem__corpo">
          <EtapaDaOrigem numero={1} titulo="No arquivo HAR">
            <ul className="painel-origem__lista">
              {biblioteca.evidencias.map((evidencia) => (
                <li key={evidencia.indice_requisicao}>
                  <dl className="painel-origem__dados">
                    <dt>Requisição</dt>
                    <dd>
                      <code>log.entries[{evidencia.indice_requisicao}]</code>
                    </dd>
                    <dt>URL</dt>
                    <dd>
                      <code>{evidencia.url}</code>
                    </dd>
                  </dl>
                </li>
              ))}
            </ul>
          </EtapaDaOrigem>

          <EtapaDaOrigem numero={2} titulo="Identificação da biblioteca">
            <dl className="painel-origem__dados">
              <dt>Método</dt>
              <dd>
                <SeloDoMetodo metodo={biblioteca.metodo} />
              </dd>
              <dt>Resultado</dt>
              <dd>
                <code>
                  {biblioteca.pacote}@{biblioteca.versao}
                </code>
              </dd>
              <dt>
                Registro do <Termo nome="npm" />
              </dt>
              <dd>{textoDoNpm(biblioteca.conferida_no_npm)}</dd>
            </dl>
            {trechosSemRepeticao(biblioteca).map((trecho) => (
              <pre key={trecho} className="painel-origem__trecho">
                {trecho}
              </pre>
            ))}
          </EtapaDaOrigem>

          <EtapaDaOrigem numero={3} titulo="Aviso nas fontes">
            {avisosNasFontes(origem)}
          </EtapaDaOrigem>

          <EtapaDaOrigem numero={4} titulo="Cálculo da nota">
            {achados.length === 0 ? (
              <p className="painel-origem__texto">
                {naoConsultada ? "Sem a consulta ao aviso, não há nota." : "Sem aviso, não há nota a calcular."}
              </p>
            ) : (
              <ul className="painel-origem__lista">
                {achados.map(({ aviso, nota }) => (
                  <li key={aviso.ghsa} className="painel-origem__conta">
                    {achados.length > 1 && <span className="painel-origem__texto">{aviso.ghsa}</span>}
                    <code className="painel-origem__formula">{nota.conta}</code>
                    <SeloDePrioridade prioridade={nota.prioridade} />
                  </li>
                ))}
              </ul>
            )}
            {achados.length > 1 && (
              <p className="painel-origem__texto">
                Nota da biblioteca:{" "}
                <b>{biblioteca.nota === null ? "sem nota" : formatarNota(biblioteca.nota)}</b>, a maior entre as
                falhas.
              </p>
            )}
          </EtapaDaOrigem>
        </div>
      </div>
    </dialog>
  );
}

function avisosNasFontes({ biblioteca, achados }: OrigemDoDado) {
  if (biblioteca.motivo_nao_consultada !== null) {
    return <p className="painel-origem__texto">Não consultado: {biblioteca.motivo_nao_consultada}.</p>;
  }
  if (achados.length === 0) {
    return <p className="painel-origem__texto">Nenhum aviso atinge esta versão.</p>;
  }
  return (
    <ul className="painel-origem__lista">
      {achados.map(({ aviso }) => (
        <li key={aviso.ghsa}>
          <dl className="painel-origem__dados">
            <dt>Aviso</dt>
            <dd>
              <a href={aviso.link} target="_blank" rel="noopener noreferrer">
                {aviso.ghsa}
              </a>
              {aviso.cve !== null && <code> · {aviso.cve}</code>}
              {fonteDoCampo(aviso, "link")}
            </dd>
            <dt>Fontes</dt>
            <dd>{aviso.fontes.join(" · ")}</dd>
            <dt>Versões afetadas</dt>
            <dd>
              <code>{aviso.versoes_afetadas}</code>
              {fonteDoCampo(aviso, "versoes_afetadas")}
            </dd>
            <dt>Corrigida em</dt>
            <dd>
              {aviso.versao_corrigida === null ? "sem versão corrigida" : <code>{aviso.versao_corrigida}</code>}
              {fonteDoCampo(aviso, "versao_corrigida")}
            </dd>
            <dt>
              <Termo nome="CVSS" />
            </dt>
            <dd>
              {aviso.cvss === null ? "sem CVSS" : formatarNota(aviso.cvss)}
              {fonteDoCampo(aviso, "cvss")}
            </dd>
            <dt>
              Percentil <Termo nome="EPSS" />
            </dt>
            <dd>
              {aviso.percentil_epss === null ? "sem EPSS" : formatarPercentil(aviso.percentil_epss)}
              {fonteDoCampo(aviso, "percentil_epss")}
            </dd>
          </dl>
        </li>
      ))}
    </ul>
  );
}

function tituloDaOrigem({ biblioteca, achados }: OrigemDoDado): string {
  const nome = `${biblioteca.pacote} ${biblioteca.versao}`;
  return achados.length === 1 ? `${nome} · ${achados[0].aviso.ghsa}` : nome;
}

function fonteDoCampo(aviso: Aviso, campo: CampoComOrigem) {
  const fonte = aviso.origem_dos_campos[campo];
  return fonte === undefined ? null : <span className="painel-origem__fonte"> · {fonte}</span>;
}

function trechosSemRepeticao(biblioteca: Biblioteca): string[] {
  const trechos = biblioteca.evidencias.map((evidencia) => evidencia.trecho);
  return [...new Set(trechos.filter((trecho) => trecho !== null))];
}

function textoDoNpm(conferida: boolean | null): string {
  if (conferida === null) {
    return "não respondeu; versão não conferida";
  }
  return conferida ? "versão publicada" : "versão não encontrada";
}
