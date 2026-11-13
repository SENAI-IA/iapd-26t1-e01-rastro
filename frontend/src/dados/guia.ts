export type IlustracaoDoPasso = "instalar" | "site" | "rede" | "cache" | "navegar" | "exportar" | "terminal" | "relatorio";

export interface Comando {
  sistema: string;
  texto: string;
}

export interface PassoDoGuia {
  titulo: string;
  texto: string;
  dica?: string;
  comandos?: Comando[];
  ilustracao: IlustracaoDoPasso;
}

export interface Problema {
  sintoma: string;
  solucao: string;
}

export const ANTES_DE_COMECAR: string[] = [
  "**Chrome ou Edge.** No Firefox os passos são os mesmos, com outros nomes de menu.",
  "**Python e a pasta do Rastro** no computador, como na seção \"Instalar\" do README.",
  "**Uma CLI de IA** (Kiro, Claude ou Codex) para a análise completa. Sem ela, rode com `--sem-ia`.",
  "**Autorização para analisar o site.** O Rastro só lê o arquivo gravado e nunca acessa o site, mas combine com o time responsável.",
];

export const PASSOS_DO_GUIA: PassoDoGuia[] = [
  {
    titulo: "Instale o comando rastro",
    texto:
      "Só na primeira vez: abra o terminal na pasta do Rastro e rode o comando. Depois disso, é só digitar `rastro` no terminal, em qualquer pasta.",
    comandos: [
      { sistema: "Linux", texto: "python3 -m rastro instalar" },
      { sistema: "Windows", texto: "py -m rastro instalar" },
    ],
    dica: "Se o terminal pedir, feche-o e abra outro. Confira com `rastro --help`. Já instalou antes? Marque como feito e siga.",
    ilustracao: "instalar",
  },
  {
    titulo: "Abra o site",
    texto:
      "No Chrome ou no Edge, abra o site que você quer analisar: o seu, ou um que você tem autorização para auditar. Prefira o ambiente de homologação.",
    ilustracao: "site",
  },
  {
    titulo: "Abra a aba Rede",
    texto: "Pressione `F12` para abrir o DevTools e clique na aba **Rede** (Network).",
    ilustracao: "rede",
  },
  {
    titulo: "Desative o cache e recarregue",
    texto:
      "Marque **Desativar cache** (Disable cache) e recarregue a página com `Ctrl + R`. Assim os scripts vêm com o conteúdo, que é onde o Rastro lê as versões.",
    dica: "Se a lista de requisições ficar vazia, recarregue de novo com o DevTools aberto.",
    ilustracao: "cache",
  },
  {
    titulo: "Navegue pelo site",
    texto:
      "Use o site como quem usa de verdade e passe pelas páginas que importam. Cada linha nova na aba Rede é um arquivo gravado.",
    dica: "Quanto mais páginas você visitar, mais bibliotecas o Rastro encontra.",
    ilustracao: "navegar",
  },
  {
    titulo: "Exporte o HAR",
    texto:
      "Clique no ícone de download da aba Rede e escolha **Exportar HAR (sanitized)**. Salve como `site.har`.",
    dica: "O sanitized sai sem cookies e cabeçalhos de autenticação e é o mais seguro. Com ele, as checagens de cookie ficam como não verificadas; para elas, exporte o HAR completo e apague o arquivo depois.",
    ilustracao: "exportar",
  },
  {
    titulo: "Rode o Rastro",
    texto:
      "Abra o terminal na pasta onde salvou o `site.har` e rode o comando. Com IA, cada chamada pode levar até 2 minutos; no fim, o terminal mostra o resumo e onde gravou o relatório.",
    comandos: [
      { sistema: "Linux", texto: "rastro analisar site.har" },
      { sistema: "Windows", texto: "rastro analisar site.har" },
    ],
    dica: "Sem CLI de IA, acrescente `--sem-ia`: nota, prioridade e plano são os mesmos, mas bibliotecas em bundles não são procuradas e os achados ficam sem explicação.",
    ilustracao: "terminal",
  },
  {
    titulo: "Abra o relatório",
    texto:
      "Abra o `relatorio.html` com dois cliques: ele funciona sem internet. Comece pela **primeira ação** e por **O que fazer agora**. Na primeira vez, clique em **Tour guiado**.",
    dica: "Cada análise fica numa pasta nova, em `Rastro/relatorios/<site>/<data e hora>/` dentro da pasta do usuário.",
    ilustracao: "relatorio",
  },
];

export const PROBLEMAS: Problema[] = [
  {
    sintoma: "A aba Rede está vazia",
    solucao: "O DevTools precisa estar aberto antes de a página carregar. Recarregue com `Ctrl + R`.",
  },
  {
    sintoma: "O relatório diz que nenhuma resposta trouxe conteúdo JavaScript",
    solucao: "O HAR foi gravado sem o conteúdo dos scripts, quase sempre por causa do cache. Marque **Desativar cache**, recarregue e exporte o HAR de novo.",
  },
  {
    sintoma: "As checagens de cookie estão como não verificadas",
    solucao: "É o esperado com o HAR sanitized, que tira os cookies. As bibliotecas são analisadas do mesmo jeito.",
  },
  {
    sintoma: "\"rastro: comando não encontrado\"",
    solucao: "Feche o terminal e abra outro. Se continuar, rode de novo `python3 -m rastro instalar` na pasta do Rastro (Windows: `py -m rastro instalar`). Se mudou a pasta do Rastro de lugar, rode também.",
  },
  {
    sintoma: "\"A CLI da IA não foi encontrada\"",
    solucao: "Instale a CLI, escolha outra IA com `--ia claude` ou rode com `--sem-ia`.",
  },
  {
    sintoma: "\"A pasta da análise já existe\"",
    solucao: "O Rastro nunca sobrescreve um relatório. Rode de novo ou escolha outra pasta com `--saida`.",
  },
];

export const SEUS_DADOS: string[] = [
  "O HAR e o relatório ficam na sua máquina, e o site analisado nunca é acessado.",
  "A IA recebe só trechos de scripts, o nome e a versão das bibliotecas e os dados dos avisos, com tokens, chaves e parâmetros de endereço tirados antes.",
  "O GitHub Advisory, o OSV e o registro do npm recebem só o nome e a versão das bibliotecas; o NVD, só o CVE.",
];
