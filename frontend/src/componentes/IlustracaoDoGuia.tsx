import type { ReactNode } from "react";
import type { IlustracaoDoPasso } from "../dados/guia.ts";
import "./IlustracaoDoGuia.css";

function janela(conteudo: ReactNode): ReactNode {
  return (
    <>
      <rect className="ilustracao__traco" x="8" y="8" width="304" height="174" rx="4" />
      <line className="ilustracao__traco" x1="8" y1="34" x2="312" y2="34" />
      <circle className="ilustracao__traco" cx="22" cy="21" r="4" />
      <circle className="ilustracao__traco" cx="34" cy="21" r="4" />
      <circle className="ilustracao__traco" cx="46" cy="21" r="4" />
      {conteudo}
    </>
  );
}

function terminal(conteudo: ReactNode): ReactNode {
  return (
    <>
      <rect className="ilustracao__traco" x="8" y="10" width="304" height="170" rx="4" />
      <line className="ilustracao__traco" x1="8" y1="34" x2="312" y2="34" />
      <circle className="ilustracao__traco" cx="22" cy="22" r="4" />
      <circle className="ilustracao__traco" cx="34" cy="22" r="4" />
      <circle className="ilustracao__traco" cx="46" cy="22" r="4" />
      {conteudo}
    </>
  );
}

const DESENHOS: Record<IlustracaoDoPasso, ReactNode> = {
  site: (
    janela(
      <>
      <rect className="ilustracao__traco ilustracao__traco--destaque" x="62" y="14" width="200" height="14" rx="7" />
      <text className="ilustracao__texto" x="76" y="24.5">
        loja.homologacao.local
      </text>
      <rect className="ilustracao__traco" x="24" y="48" width="272" height="52" rx="3" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="116" x2="210" y2="116" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="130" x2="160" y2="130" />
      <rect className="ilustracao__traco ilustracao__traco--destaque" x="24" y="148" width="76" height="22" rx="3" />
      <text className="ilustracao__texto ilustracao__texto--destaque" x="44" y="162.5">
        Entrar
      </text>
      <path
        className="ilustracao__traco ilustracao__traco--destaque ilustracao__cursor"
        d="M150 150 l0 18 l5 -5 l4 8 l3 -1.5 l-4 -8 l7 0 z"
      />
      </>,
    )
  ),
  rede: (
    janela(
      <>
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="52" x2="180" y2="52" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="66" x2="140" y2="66" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="80" x2="160" y2="80" />
      <line className="ilustracao__traco" x1="8" y1="98" x2="312" y2="98" />
      <text className="ilustracao__texto" x="20" y="116">
        Elementos
      </text>
      <text className="ilustracao__texto" x="84" y="116">
        Console
      </text>
      <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="140" y="116">
        Rede
      </text>
      <line className="ilustracao__traco ilustracao__traco--destaque" x1="138" y1="122" x2="166" y2="122" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="20" y1="140" x2="290" y2="140" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="20" y1="154" x2="250" y2="154" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="20" y1="168" x2="270" y2="168" />
      <g className="ilustracao__tecla">
        <rect className="ilustracao__traco ilustracao__traco--destaque" x="246" y="46" width="50" height="28" rx="3" />
        <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="260" y="64.5">
          F12
        </text>
      </g>
      </>,
    )
  ),
  cache: (
    <>
      <rect className="ilustracao__traco" x="8" y="30" width="304" height="130" rx="4" />
      <line className="ilustracao__traco" x1="8" y1="66" x2="312" y2="66" />
      <circle className="ilustracao__traco" cx="30" cy="48" r="7" />
      <rect className="ilustracao__traco ilustracao__traco--destaque" x="50" y="41" width="14" height="14" rx="2" />
      <path className="ilustracao__traco ilustracao__traco--destaque" d="M53 48 l3.5 3.5 l6 -7" />
      <text className="ilustracao__texto ilustracao__texto--forte" x="72" y="52">
        Desativar cache
      </text>
      <g className="ilustracao__giro">
        <path className="ilustracao__traco ilustracao__traco--destaque" d="M268 40 a9 9 0 1 0 8 6" />
        <path className="ilustracao__traco ilustracao__traco--destaque" d="M272 38 l4 3 l-1 5" />
      </g>
      <rect className="ilustracao__realce" x="18" y="73" width="44" height="18" rx="3" />
      <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="27" y="86">
        Todos
      </text>
      <text className="ilustracao__texto" x="74" y="86">
        Fetch/XHR
      </text>
      <text className="ilustracao__texto" x="138" y="86">
        JS
      </text>
      <text className="ilustracao__texto" x="162" y="86">
        CSS
      </text>
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="106" x2="250" y2="106" />
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="120" x2="200" y2="120" />
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="134" x2="230" y2="134" />
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="148" x2="170" y2="148" />
      <rect className="ilustracao__traco" x="196" y="168" width="104" height="16" rx="3" />
      <text className="ilustracao__texto" x="226" y="179.5">
        Ctrl + R
      </text>
    </>
  ),
  navegar: (
    janela(
      <>
      <rect className="ilustracao__traco" x="24" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco" x="92" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco" x="160" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco ilustracao__traco--suave" x="24" y="70" width="272" height="30" rx="3" />
      <path
        className="ilustracao__traco ilustracao__traco--destaque ilustracao__passeio"
        d="M60 52 l0 16 l4.5 -4.5 l3.5 7 l2.7 -1.3 l-3.5 -7 l6.3 0 z"
      />
      <line className="ilustracao__traco" x1="8" y1="110" x2="312" y2="110" />
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="126" x2="210" y2="126" />
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="140" x2="250" y2="140" />
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="154" x2="180" y2="154" />
      <line className="ilustracao__linha" pathLength="1" x1="22" y1="168" x2="230" y2="168" />
      </>,
    )
  ),
  exportar: (
    <>
      <rect className="ilustracao__traco" x="8" y="18" width="304" height="58" rx="4" />
      <circle className="ilustracao__traco" cx="30" cy="47" r="7" />
      <rect className="ilustracao__traco" x="50" y="40" width="14" height="14" rx="2" />
      <text className="ilustracao__texto" x="72" y="51">
        Desativar cache
      </text>
      <g className="ilustracao__pulo">
        <path className="ilustracao__traco ilustracao__traco--destaque" d="M276 36 v16 M269 46 l7 7 l7 -7" />
        <line className="ilustracao__traco ilustracao__traco--destaque" x1="267" y1="60" x2="285" y2="60" />
      </g>
      <rect className="ilustracao__traco" x="112" y="86" width="192" height="64" rx="4" />
      <rect className="ilustracao__realce" x="118" y="92" width="180" height="24" rx="3" />
      <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="128" y="108">
        Exportar HAR (sanitized)
      </text>
      <text className="ilustracao__texto" x="128" y="136">
        Exportar HAR (completo)
      </text>
      <path className="ilustracao__traco ilustracao__traco--destaque" d="M26 96 h34 l12 12 v50 h-46 z M60 96 v12 h12" />
      <text className="ilustracao__texto ilustracao__texto--forte" x="24" y="176">
        site.har
      </text>
    </>
  ),
  instalar: terminal(
    <>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--forte ilustracao__digita ilustracao__digita--1" x="22" y="60">
        $ python3 -m rastro instalar
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--2" x="22" y="84">
        Pronto! Comando rastro instalado.
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--3" x="22" y="102">
        Abra um terminal novo e teste.
      </text>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--4"
        x="22"
        y="128"
      >
        $ rastro --help
      </text>
      <rect className="ilustracao__cursor-texto" x="22" y="138" width="7" height="12" />
    </>,
  ),
  playwright: terminal(
    <>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--forte ilustracao__digita ilustracao__digita--1" x="22" y="60">
        $ python3 -m pip install --user
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--forte ilustracao__digita ilustracao__digita--1" x="22" y="78">
            playwright==1.65.1
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--2" x="22" y="102">
        Collecting playwright==1.65.1
      </text>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--3"
        x="22"
        y="128"
      >
        Successfully installed playwright
      </text>
      <rect className="ilustracao__cursor-texto" x="22" y="138" width="7" height="12" />
    </>,
  ),
  gravar: terminal(
    <>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--forte ilustracao__digita ilustracao__digita--1" x="22" y="60">
        $ rastro gravar https://site.com.br
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--2" x="22" y="84">
        Navegue e feche a janela para analisar.
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--3" x="22" y="102">
        Gravação em: ~/Rastro/gravacoes/
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--4" x="22" y="120">
        Requisições gravadas: 214
      </text>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--5"
        x="22"
        y="146"
      >
        HTML: …/relatorio.html
      </text>
      <rect className="ilustracao__cursor-texto" x="22" y="156" width="7" height="12" />
    </>,
  ),
  robo: terminal(
    <>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--forte ilustracao__digita ilustracao__digita--1" x="22" y="60">
        $ rastro gravar https://site.com.br --robo
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--2" x="22" y="84">
        Entre, se precisar, e aperte Enter.
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--3" x="22" y="102">
        [1/20] 12 req · 3 scripts · /
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--4" x="22" y="120">
        [2/20] 18 req · 1 script · /produtos
      </text>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--5"
        x="22"
        y="146"
      >
        Parou: nenhum link novo.
      </text>
      <rect className="ilustracao__cursor-texto" x="22" y="156" width="7" height="12" />
    </>,
  ),
  terminal: terminal(
    <>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--forte ilustracao__digita ilustracao__digita--1" x="22" y="60">
        $ rastro analisar site.har
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--2" x="22" y="84">
        Análise com a IA kiro.
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--3" x="22" y="102">
        Relatório gravado em: ~/Rastro/relatorios/
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--4" x="22" y="120">
        Resumo: bibliotecas: 6 · achados: 20
      </text>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--5"
        x="22"
        y="146"
      >
        HTML: …/relatorio.html
      </text>
      <rect className="ilustracao__cursor-texto" x="22" y="156" width="7" height="12" />
    </>,
  ),
  entrar: (
    <>
      <rect className="ilustracao__traco" x="8" y="18" width="172" height="154" rx="4" />
      <line className="ilustracao__traco" x1="8" y1="42" x2="180" y2="42" />
      <circle className="ilustracao__traco" cx="22" cy="30" r="4" />
      <circle className="ilustracao__traco" cx="34" cy="30" r="4" />
      <text className="ilustracao__texto" x="50" y="33.5">
        Navegador
      </text>
      <text className="ilustracao__texto ilustracao__texto--forte" x="24" y="64">
        Entrar no site
      </text>
      <rect className="ilustracao__traco" x="24" y="74" width="140" height="20" rx="3" />
      <text className="ilustracao__texto ilustracao__digita ilustracao__digita--1" x="32" y="88">
        maria@empresa.com
      </text>
      <rect className="ilustracao__traco" x="24" y="102" width="140" height="20" rx="3" />
      <text className="ilustracao__texto ilustracao__digita ilustracao__digita--2" x="32" y="117">
        ••••••••
      </text>
      <rect className="ilustracao__traco ilustracao__traco--destaque" x="24" y="134" width="64" height="22" rx="3" />
      <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="40" y="148.5">
        Entrar
      </text>
      <path
        className="ilustracao__traco ilustracao__traco--destaque ilustracao__digita ilustracao__digita--3"
        d="M82 150 l0 16 l4.5 -4.5 l3.5 7 l2.7 -1.3 l-3.5 -7 l6.3 0 z"
      />
      <rect className="ilustracao__traco" x="192" y="18" width="120" height="154" rx="4" />
      <line className="ilustracao__traco" x1="192" y1="42" x2="312" y2="42" />
      <text className="ilustracao__texto" x="204" y="33.5">
        Terminal
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--1" x="202" y="64">
        Entre e aperte
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--1" x="202" y="78">
        Enter.
      </text>
      <g className="ilustracao__digita ilustracao__digita--4">
        <g className="ilustracao__tecla">
          <rect className="ilustracao__traco ilustracao__traco--destaque" x="216" y="94" width="72" height="28" rx="4" />
          <text className="ilustracao__texto ilustracao__texto--destaque ilustracao__texto--forte" x="238" y="112.5">
            Enter
          </text>
        </g>
      </g>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--5"
        x="202"
        y="150"
      >
        [1/20] /
      </text>
    </>
  ),
  "robo-visita": (
    janela(
      <>
      <rect className="ilustracao__traco ilustracao__traco--destaque" x="62" y="14" width="200" height="14" rx="7" />
      <text className="ilustracao__texto" x="76" y="24.5">
        site.com.br
      </text>
      <rect className="ilustracao__traco" x="24" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco" x="92" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco" x="160" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco" x="24" y="72" width="128" height="34" rx="3" />
      <rect className="ilustracao__traco" x="160" y="72" width="136" height="34" rx="3" />
      <g transform="translate(54 54)">
        <g className="ilustracao__robo">
          <line className="ilustracao__traco ilustracao__traco--destaque" x1="0" y1="-8" x2="0" y2="-13" />
          <circle className="ilustracao__olho" cx="0" cy="-14.5" r="2" />
          <rect className="ilustracao__traco ilustracao__traco--destaque ilustracao__cabeca" x="-10" y="-8" width="20" height="16" rx="3" />
          <circle className="ilustracao__olho" cx="-4" cy="0" r="2" />
          <circle className="ilustracao__olho" cx="4" cy="0" r="2" />
        </g>
      </g>
      <line className="ilustracao__traco" x1="8" y1="116" x2="312" y2="116" />
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--2" x="22" y="134">
        [1/20] /
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--3" x="22" y="150">
        [2/20] /produtos
      </text>
      <text className="ilustracao__texto ilustracao__texto--mono ilustracao__digita ilustracao__digita--4" x="22" y="166">
        [3/20] /contato
      </text>
      <text
        className="ilustracao__texto ilustracao__texto--mono ilustracao__texto--destaque ilustracao__texto--forte ilustracao__digita ilustracao__digita--5"
        x="170"
        y="166"
      >
        Parou: fim dos links
      </text>
      </>,
    )
  ),
  "navegar-e-fechar": (
    janela(
      <>
      <g className="ilustracao__pulsa-fechar">
        <circle className="ilustracao__traco ilustracao__traco--destaque" cx="296" cy="21" r="7" />
        <path className="ilustracao__traco ilustracao__traco--destaque" d="M292.5 17.5 l7 7 M299.5 17.5 l-7 7" />
      </g>
      <rect className="ilustracao__traco" x="24" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco" x="92" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco" x="160" y="46" width="60" height="16" rx="3" />
      <rect className="ilustracao__traco ilustracao__traco--suave" x="24" y="76" width="272" height="30" rx="3" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="128" x2="250" y2="128" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="144" x2="210" y2="144" />
      <line className="ilustracao__traco ilustracao__traco--suave" x1="24" y1="160" x2="230" y2="160" />
      <path
        className="ilustracao__traco ilustracao__traco--destaque ilustracao__cabeca ilustracao__vai-fechar"
        d="M60 52 l0 16 l4.5 -4.5 l3.5 7 l2.7 -1.3 l-3.5 -7 l6.3 0 z"
      />
      </>,
    )
  ),
  relatorio: (
    janela(
      <>
      <rect className="ilustracao__traco ilustracao__traco--destaque ilustracao__pulsa" x="22" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao__traco" x="92" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao__traco" x="162" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao__traco" x="232" y="46" width="64" height="34" rx="3" />
      <rect className="ilustracao__traco" x="22" y="90" width="166" height="80" rx="3" />
      <circle className="ilustracao__traco" cx="105" cy="130" r="32" />
      <circle className="ilustracao__traco" cx="105" cy="130" r="20" />
      <circle className="ilustracao__traco ilustracao__traco--destaque" cx="128" cy="112" r="4" />
      <circle className="ilustracao__traco ilustracao__traco--destaque" cx="90" cy="146" r="4" />
      <rect className="ilustracao__traco" x="196" y="90" width="100" height="80" rx="3" />
      <line className="ilustracao__traco ilustracao__traco--destaque ilustracao__traco--grosso" x1="206" y1="106" x2="284" y2="106" />
      <line className="ilustracao__traco ilustracao__traco--destaque ilustracao__traco--grosso" x1="206" y1="122" x2="252" y2="122" />
      <line className="ilustracao__traco ilustracao__traco--destaque ilustracao__traco--grosso" x1="206" y1="138" x2="232" y2="138" />
      <line className="ilustracao__traco ilustracao__traco--destaque ilustracao__traco--grosso" x1="206" y1="154" x2="214" y2="154" />
      </>,
    )
  ),
};

interface Props {
  ilustracao: IlustracaoDoPasso;
}

export default function IlustracaoDoGuia({ ilustracao }: Props) {
  return (
    <svg className="ilustracao" viewBox="0 0 320 190" aria-hidden="true">
      {DESENHOS[ilustracao]}
    </svg>
  );
}
