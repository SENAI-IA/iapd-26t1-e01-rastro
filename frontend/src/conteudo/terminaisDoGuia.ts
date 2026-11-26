import type { LinhaDoTerminal } from "../calculosDeTela/linhasDoTerminal.ts";

export type TerminalDoGuia = "instalar" | "playwright" | "gravar" | "robo" | "terminal" | "pentest";

export const LINHAS_DO_TERMINAL: Record<TerminalDoGuia, LinhaDoTerminal[]> = {
  instalar: [
    { texto: "$ curl …/install.sh | bash", destaque: "comando" },
    { texto: "Pronto! Comando rastro instalado.", destaque: "saida" },
    { texto: "Abra um terminal novo e teste.", destaque: "saida" },
    { texto: "$ rastro --help", destaque: "resultado" },
  ],
  playwright: [
    { texto: "$ python3 -m pip install --user", destaque: "comando" },
    { texto: "playwright==1.65.1", destaque: "continuacao" },
    { texto: "Collecting playwright==1.65.1", destaque: "saida" },
    { texto: "Successfully installed playwright", destaque: "resultado" },
  ],
  gravar: [
    { texto: "$ rastro gravar https://site.com.br", destaque: "comando" },
    { texto: "Navegue e feche a janela para analisar.", destaque: "saida" },
    { texto: "Gravação em: ~/Rastro/gravacoes/", destaque: "saida" },
    { texto: "Requisições gravadas: 214", destaque: "saida" },
    { texto: "HTML: …/relatorio.html", destaque: "resultado" },
  ],
  robo: [
    { texto: "$ rastro gravar https://site.com.br --robo", destaque: "comando" },
    { texto: "Entre, se precisar, e aperte Enter.", destaque: "saida" },
    { texto: "[1/20] 12 req · 3 scripts · /", destaque: "saida" },
    { texto: "[2/20] 18 req · 1 script · /produtos", destaque: "saida" },
    { texto: "Parou: nenhum link novo.", destaque: "resultado" },
  ],
  terminal: [
    { texto: "$ rastro analisar site.har", destaque: "comando" },
    { texto: "Análise com a IA kiro.", destaque: "saida" },
    { texto: "Relatório gravado em: ~/Rastro/relatorios/", destaque: "saida" },
    { texto: "Resumo: bibliotecas: 6 · achados: 20", destaque: "saida" },
    { texto: "HTML: …/relatorio.html", destaque: "resultado" },
  ],
  pentest: [
    { texto: "$ rastro pentest site.har --autorizo", destaque: "comando" },
    { texto: "Resumo: 7 falharam, 9 passaram…", destaque: "saida" },
    { texto: "Escopo: configuração de segurança…", destaque: "saida" },
    { texto: "Pentest gravado em: …/pentest.json", destaque: "resultado" },
  ],
};
