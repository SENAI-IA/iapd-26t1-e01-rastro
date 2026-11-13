import type { NomeDoTermo } from "./glossario.ts";

export interface PassoDoTour {
  seletor: string;
  titulo: string;
  texto: string;
  termos?: NomeDoTermo[];
}

export const PASSOS_DO_TOUR: PassoDoTour[] = [
  {
    seletor: ".cabecalho-analise",
    titulo: "Uma análise do Rastro",
    texto:
      "Você grava a navegação do site e o Rastro mostra o que está vulnerável nas bibliotecas que chegaram ao navegador. O Rastro não acessa o site: tudo sai do arquivo gravado.",
    termos: ["HAR"],
  },
  {
    seletor: ".replay",
    titulo: "A visita, tocada de novo",
    texto:
      "Cada ponto é um arquivo que o navegador baixou, na ordem em que chegou. As bibliotecas com falha aparecem no momento em que entraram. Clique numa delas para abrir os detalhes.",
  },
  {
    seletor: ".indicadores",
    titulo: "O essencial em quatro números",
    texto:
      "O risco do site, quantas bibliotecas precisam de atualização, o que só a IA encontrou e qual é a primeira ação a fazer.",
    termos: ["Bundle"],
  },
  {
    seletor: ".painel-ia",
    titulo: "Onde a IA entrou",
    texto:
      "A IA procura bibliotecas escondidas e explica os achados, mas não decide nada sozinha: travas fixas conferem o que ela sugere. Aqui ficam as chamadas, o tempo, os tokens e o que cada trava barrou.",
    termos: ["Trava"],
  },
  {
    seletor: ".plano-de-acao",
    titulo: "O que fazer agora",
    texto:
      "As correções em ordem de prioridade. Cada uma diz o porquê, o impacto, quem resolve e como conferir que deu certo.",
  },
  {
    seletor: ".acao__abrir-task",
    titulo: "A task pronta para o time",
    texto:
      "Um clique abre o texto da task, com título, evidências, o que fazer e o critério de aceite. Copie e cole no Azure DevOps ou no GitLab.",
  },
  {
    seletor: ".lista-bibliotecas__lista",
    titulo: "Cada biblioteca, com as falhas",
    texto:
      "Abra uma biblioteca para ver as falhas, a explicação e onde ela apareceu no arquivo. \"Ver a origem\" mostra de onde veio cada dado e a conta da nota.",
    termos: ["CVSS", "EPSS"],
  },
  {
    seletor: ".lista-a-confirmar",
    titulo: "O que ficou a confirmar",
    texto:
      "Bibliotecas que uma trava não deixou passar. Não entram na nota nem no plano, mas também não somem: cada uma diz a trava que falhou e como conferir à mão.",
    termos: ["npm"],
  },
  {
    seletor: ".lista-checagens",
    titulo: "A configuração do servidor",
    texto:
      "Do mesmo arquivo saem as checagens de cabeçalhos de segurança e de cookies, inclusive as que passaram. Com o HAR sanitized, as de cookie ficam como não verificadas.",
  },
  {
    seletor: ".zona__focar",
    titulo: "Uma zona por vez",
    texto: "\"Focar\" mostra só aquela zona, usando a tela toda. Esc ou \"Sair do foco\" volta ao relatório completo.",
  },
  {
    seletor: ".termo",
    titulo: "Dúvida em algum termo?",
    texto:
      "Palavras com sublinhado pontilhado têm explicação simples. Passe o mouse, toque ou chegue nelas pelo teclado a qualquer momento.",
  },
];
