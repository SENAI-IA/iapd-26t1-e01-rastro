export type TerminalDoGuia = "instalar" | "playwright" | "gravar" | "robo" | "terminal" | "pentest";

export type TomDaSaida = "fraco" | "forte" | "destaque" | "bom" | "aviso";

export type LinhaDaSimulacao =
  | { comando: string }
  | { etapa: string; tempo: string; espera?: number }
  | { pergunta: string; resposta: string }
  | { saida: string; tom?: TomDaSaida; espera?: number };

export interface SimulacaoDoPasso {
  previa: LinhaDaSimulacao[];
  completa: LinhaDaSimulacao[];
}

const COMANDO_DE_INSTALAR = "curl -fsSL https://raw.githubusercontent.com/SENAI-IA/iapd-26t1-e01-rastro/main/install.sh | bash";
const COMANDO_DO_PLAYWRIGHT = "python3 -m pip install --user playwright==1.65.1";
const PASTA_DO_RELATORIO = "~/Rastro/relatorios/site.com.br/2026-11-27_09-44-29";

const ETAPAS_DA_ANALISE: LinhaDaSimulacao[] = [
  { etapa: "[1/7] Lendo o HAR", tempo: "0:00", espera: 500 },
  { etapa: "[2/7] Reconhecendo as bibliotecas pelos arquivos", tempo: "0:01", espera: 600 },
  { etapa: "[3/7] Procurando bibliotecas nos bundles com a IA · 6 de 6", tempo: "1:04", espera: 2200 },
  { etapa: "[4/7] Conferindo as bibliotecas no npm · 4 de 4", tempo: "0:02", espera: 700 },
  { etapa: "[5/7] Consultando falhas conhecidas (GitHub, OSV, NVD) · 4 de 4", tempo: "0:03", espera: 900 },
  { etapa: "[6/7] Explicando os achados com a IA · 1 de 1", tempo: "0:15", espera: 1400 },
  { etapa: "[7/7] Conferindo a configuração e montando o plano de ação", tempo: "0:00", espera: 500 },
];

const FIM_DA_ANALISE: LinhaDaSimulacao[] = [
  { saida: `Relatório gravado em: ${PASTA_DO_RELATORIO}` },
  { saida: `HTML: ${PASTA_DO_RELATORIO}/relatorio.html`, tom: "destaque" },
  { saida: "Resumo: site.com.br · bibliotecas: 4 (1 com falhas) · achados: 4 · nota máxima: 8,4", tom: "forte" },
];

export const SIMULACOES_DO_GUIA: Record<TerminalDoGuia, SimulacaoDoPasso> = {
  instalar: {
    previa: [
      { comando: COMANDO_DE_INSTALAR },
      { saida: "Pronto! Comando rastro instalado.", tom: "bom" },
      { saida: "Abra um terminal novo e teste com: rastro --help", tom: "destaque" },
    ],
    completa: [
      { comando: COMANDO_DE_INSTALAR },
      { saida: "Baixando o Rastro para ~/.local/share/rastro ...", espera: 1200 },
      { saida: "Pronto! Comando rastro instalado.", tom: "bom" },
      { saida: "Abra um terminal novo e teste com: rastro --help", tom: "destaque" },
      { saida: "Os arquivos do Rastro ficam em ~/.local/share/rastro. Para atualizar, rode este instalador de novo.", tom: "fraco" },
      { comando: "rastro --help" },
      { saida: "usage: rastro [-h] comando ..." },
      { saida: "  analisar · gravar · pentest · como-usar · instalar · desinstalar", tom: "fraco" },
    ],
  },
  playwright: {
    previa: [
      { comando: COMANDO_DO_PLAYWRIGHT },
      { saida: "Collecting playwright==1.65.1", tom: "fraco" },
      { saida: "Successfully installed playwright-1.65.1", tom: "bom" },
    ],
    completa: [
      { comando: COMANDO_DO_PLAYWRIGHT },
      { saida: "Collecting playwright==1.65.1", tom: "fraco", espera: 700 },
      { saida: "  Downloading playwright-1.65.1-py3-none-manylinux1_x86_64.whl (45.2 MB)", tom: "fraco", espera: 1400 },
      { saida: "Installing collected packages: playwright", tom: "fraco", espera: 900 },
      { saida: "Successfully installed playwright-1.65.1", tom: "bom" },
    ],
  },
  gravar: {
    previa: [
      { comando: "rastro gravar https://site.com.br" },
      { saida: "Visita gravada em: ~/Rastro/gravacoes/site.com.br.har" },
      { etapa: "[7/7] Conferindo a configuração e montando o plano de ação", tempo: "0:00" },
      { saida: "HTML: …/relatorio.html", tom: "destaque" },
    ],
    completa: [
      { comando: "rastro gravar https://site.com.br" },
      { etapa: "Abrindo o navegador", tempo: "0:02", espera: 900 },
      { saida: "Gravando a visita a site.com.br. Navegue pelo site como um usuário comum e feche a janela quando terminar (ou aperte Ctrl+C aqui).", tom: "aviso" },
      { etapa: "Gravando · requisições 214 · scripts 31 · feche a janela para analisar", tempo: "2:36", espera: 2400 },
      { etapa: "Salvando a gravação", tempo: "0:01", espera: 600 },
      { saida: "Visita gravada em: ~/Rastro/gravacoes/site.com.br.har" },
      { saida: "Atenção: este HAR guarda a sessão do site (cabeçalhos Cookie e Set-Cookie). Não compartilhe o arquivo.", tom: "fraco" },
      { saida: "Análise com a IA kiro. Cada chamada à IA pode levar até 2 minutos." },
      ...ETAPAS_DA_ANALISE,
      ...FIM_DA_ANALISE,
    ],
  },
  robo: {
    previa: [
      { comando: "rastro gravar https://site.com.br --robo" },
      { saida: "  páginas 2/20 · requisições 61 · scripts 9 · 0:14 · /produtos", tom: "fraco" },
      { saida: "O robô parou: nenhum link novo. 8 páginas visitadas.", tom: "forte" },
    ],
    completa: [
      { comando: "rastro gravar https://site.com.br --robo" },
      { etapa: "Abrindo o navegador", tempo: "0:02", espera: 900 },
      { saida: "Cuidado em sistema de produção: o robô só segue links, mas um link comum pode disparar uma ação.", tom: "fraco" },
      { pergunta: "Se o site pede login, entre agora na janela aberta e depois aperte Enter aqui. ", resposta: "⏎" },
      { saida: "O robô vai navegar pelos links de site.com.br: até 20 páginas, 3 minutos e 3 cliques da página inicial." },
      { saida: "  páginas 1/20 · requisições 43 · scripts 7 · 0:05 · /", tom: "fraco", espera: 700 },
      { saida: "  páginas 2/20 · requisições 61 · scripts 9 · 0:14 · /produtos", tom: "fraco", espera: 700 },
      { saida: "  páginas 3/20 · requisições 70 · scripts 9 · 0:21 · /contato", tom: "fraco", espera: 700 },
      { saida: "O robô parou: nenhum link novo. 8 páginas visitadas, 2 links perigosos ou de fora do site não seguidos.", tom: "forte" },
      { saida: "A janela continua aberta: visite mais alguma página importante e feche a janela para analisar.", tom: "aviso" },
      { etapa: "Salvando a gravação", tempo: "0:01", espera: 600 },
      { saida: "Visita gravada em: ~/Rastro/gravacoes/site.com.br.har" },
      ...ETAPAS_DA_ANALISE,
      ...FIM_DA_ANALISE,
    ],
  },
  terminal: {
    previa: [
      { comando: "rastro analisar site.har" },
      { etapa: "[7/7] Conferindo a configuração e montando o plano de ação", tempo: "0:00" },
      { saida: "HTML: …/relatorio.html", tom: "destaque" },
      { saida: "Resumo: bibliotecas: 4 (1 com falhas) · achados: 4", tom: "forte" },
    ],
    completa: [
      { comando: "rastro analisar site.har" },
      { saida: "Análise com a IA kiro. Cada chamada à IA pode levar até 2 minutos; o que ela sugere passa pelas travas antes do relatório." },
      ...ETAPAS_DA_ANALISE,
      ...FIM_DA_ANALISE,
    ],
  },
  pentest: {
    previa: [
      { comando: "rastro pentest site.har --autorizo" },
      { saida: "Resumo: 74 falharam, 121 passaram, 0 não verificadas…", tom: "forte" },
      { saida: "Pentest gravado em: …/pentest.json", tom: "destaque" },
    ],
    completa: [
      { comando: "rastro pentest site.har --autorizo" },
      { saida: "Validações de segurança ativas executadas pelo Rastro com autorização explícita. Ele usa somente GET, HEAD e OPTIONS, sem corpo, cookies ou cabeçalhos de autenticação.", tom: "fraco", espera: 1600 },
      { saida: "Site: site.com.br · requisições enviadas: 20" },
      { saida: "Resumo: 74 falharam, 121 passaram, 0 não verificadas, 177 requisições ignoradas", tom: "forte" },
      { saida: "Escopo: configuração de segurança das respostas, conforme o guia OWASP WSTG.", tom: "fraco" },
      { saida: "Pentest gravado em: ~/Rastro/pentest/site.com.br/2026-11-27_10-02-11/pentest.json", tom: "destaque" },
      { comando: "rastro analisar site.har --pentest ~/Rastro/pentest/site.com.br/2026-11-27_10-02-11/pentest.json" },
      ...ETAPAS_DA_ANALISE,
      ...FIM_DA_ANALISE,
    ],
  },
};

export function ehTerminalDoGuia(ilustracao: string): ilustracao is TerminalDoGuia {
  return Object.hasOwn(SIMULACOES_DO_GUIA, ilustracao);
}
