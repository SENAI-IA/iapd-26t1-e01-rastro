export type IlustracaoDoPasso =
  | "instalar"
  | "playwright"
  | "site"
  | "rede"
  | "cache"
  | "navegar"
  | "exportar"
  | "terminal"
  | "gravar"
  | "robo"
  | "entrar"
  | "robo-visita"
  | "navegar-e-fechar"
  | "relatorio";

export type ModoDeUso = "devtools" | "gravar" | "robo";

export interface OpcaoDeModo {
  modo: ModoDeUso;
  titulo: string;
  resumo: string;
}

export interface Item {
  texto: string;
  modos?: ModoDeUso[];
}

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
  modos?: ModoDeUso[];
}

export function valeNoModo(item: { modos?: ModoDeUso[] }, modo: ModoDeUso): boolean {
  return !item.modos || item.modos.includes(modo);
}

const GRAVANDO_PELO_RASTRO: ModoDeUso[] = ["gravar", "robo"];

export const MODOS_DE_USO: OpcaoDeModo[] = [
  {
    modo: "devtools",
    titulo: "Gravo no navegador",
    resumo: "Você grava o arquivo no DevTools do Chrome ou do Edge e entrega ao Rastro.",
  },
  {
    modo: "gravar",
    titulo: "O Rastro grava",
    resumo: "O Rastro abre o navegador, você navega e ele grava e analisa sozinho.",
  },
  {
    modo: "robo",
    titulo: "O robô navega",
    resumo: "O Rastro abre o navegador e visita os links do site por você.",
  },
];

export const ANTES_DE_COMECAR: Item[] = [
  { texto: "**Chrome ou Edge.** No Firefox os passos são os mesmos, com outros nomes de menu.", modos: ["devtools"] },
  { texto: "**Chrome ou Edge** instalado. O Rastro usa o navegador do computador.", modos: GRAVANDO_PELO_RASTRO },
  { texto: "**Python e a pasta do Rastro** no computador, como na seção \"Instalar\" do README." },
  { texto: "**Uma CLI de IA** (Kiro, Claude ou Codex) para a análise completa. Sem ela, rode com `--sem-ia`." },
  {
    texto: "**Autorização para analisar o site.** O Rastro só lê o arquivo gravado e não acessa o site, mas combine com o time responsável.",
    modos: ["devtools"],
  },
  {
    texto: "**Autorização para analisar o site.** Quem acessa o site é o navegador aberto pelo Rastro. Combine com o time responsável e prefira o ambiente de homologação.",
    modos: GRAVANDO_PELO_RASTRO,
  },
];

const INSTALAR_O_RASTRO: PassoDoGuia = {
  titulo: "Instale o comando rastro",
  texto:
    "Só na primeira vez: abra o terminal na pasta do Rastro e rode o comando. Depois disso, é só digitar `rastro` no terminal, em qualquer pasta.",
  comandos: [
    { sistema: "Linux", texto: "python3 -m rastro instalar" },
    { sistema: "Windows", texto: "py -m rastro instalar" },
  ],
  dica: "Se o terminal pedir, feche-o e abra outro. Confira com `rastro --help`. Já instalou antes? Marque como feito e siga.",
  ilustracao: "instalar",
};

const INSTALAR_O_PLAYWRIGHT: PassoDoGuia = {
  titulo: "Instale o Playwright",
  texto: "Só na primeira vez. É o que deixa o Rastro abrir e controlar o Chrome ou o Edge.",
  comandos: [
    { sistema: "Linux", texto: "python3 -m pip install --user playwright==1.65.1" },
    { sistema: "Windows", texto: "py -m pip install --user playwright==1.65.1" },
  ],
  dica: "Deu erro? Siga para o próximo passo: se faltar o Playwright, o Rastro mostra o comando certo para o seu computador.",
  ilustracao: "playwright",
};

const ABRIR_O_RELATORIO: PassoDoGuia = {
  titulo: "Abra o relatório",
  texto:
    "O relatório abre sozinho no navegador ao fim da análise e funciona sem internet. Para abrir de novo, dê dois cliques no `relatorio.html`. Comece pela **primeira ação** e por **O que fazer agora**. Na primeira vez, clique em **Tour guiado**.",
  dica: "Cada análise fica numa pasta nova, em `Rastro/relatorios/<site>/<data e hora>/` dentro da pasta do usuário.",
  ilustracao: "relatorio",
};

const ABRIR_O_RELATORIO_GRAVADO: PassoDoGuia = {
  titulo: "Abra o relatório",
  texto:
    "Ao fechar a janela, o Rastro analisa o que foi gravado e abre o relatório no navegador. Com IA, pode levar alguns minutos: o terminal mostra a etapa e o tempo, e enquanto o sinal no fim da linha girar, o Rastro está trabalhando. Comece pela **primeira ação** e por **O que fazer agora**. Na primeira vez, clique em **Tour guiado**.",
  dica: "A gravação fica em `Rastro/gravacoes/` e o relatório em `Rastro/relatorios/`, dentro da pasta do usuário.",
  ilustracao: "relatorio",
};

const PASSOS_PELO_DEVTOOLS: PassoDoGuia[] = [
  INSTALAR_O_RASTRO,
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
      "Marque **Desativar cache** (Disable cache), deixe o filtro em **Todos** (All) e recarregue a página com `Ctrl + R`. Assim os scripts vêm com o conteúdo, que é onde o Rastro lê as versões.",
    dica: "O HAR só leva o que aparece na lista: com o filtro em Fetch/XHR, por exemplo, ele sai sem nenhum script. Se a lista ficar vazia, recarregue de novo com o DevTools aberto.",
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
      "Abra o terminal na pasta onde salvou o `site.har` e rode o comando. Com IA, pode levar alguns minutos: o terminal mostra a etapa e o tempo, e enquanto o sinal no fim da linha girar, o Rastro está trabalhando. No fim, ele mostra o resumo e onde gravou o relatório.",
    comandos: [
      { sistema: "Linux", texto: "rastro analisar site.har" },
      { sistema: "Windows", texto: "rastro analisar site.har" },
    ],
    dica: "Sem CLI de IA, acrescente `--sem-ia`: nota, prioridade e plano são os mesmos, mas bibliotecas em bundles não são procuradas e os achados ficam sem explicação.",
    ilustracao: "terminal",
  },
  ABRIR_O_RELATORIO,
];

const PASSOS_COM_O_RASTRO_GRAVANDO: PassoDoGuia[] = [
  INSTALAR_O_RASTRO,
  INSTALAR_O_PLAYWRIGHT,
  {
    titulo: "Comece a gravar",
    texto:
      "Rode o comando trocando o endereço pelo do site que você quer analisar. O Chrome (ou o Edge) abre sozinho nesse site.",
    comandos: [
      { sistema: "Linux", texto: "rastro gravar https://site.com.br" },
      { sistema: "Windows", texto: "rastro gravar https://site.com.br" },
    ],
    dica: "Sem CLI de IA, acrescente `--sem-ia` no fim do comando.",
    ilustracao: "gravar",
  },
  {
    titulo: "Navegue e feche a janela",
    texto:
      "Use o site como quem usa de verdade e passe pelas páginas que importam. O terminal mostra o tempo e quantas requisições já foram gravadas. Quando terminar, feche a janela do navegador.",
    dica: "Quanto mais páginas você visitar, mais bibliotecas o Rastro encontra. Também dá para parar com `Ctrl + C` no terminal.",
    ilustracao: "navegar-e-fechar",
  },
  ABRIR_O_RELATORIO_GRAVADO,
];

const PASSOS_COM_O_ROBO: PassoDoGuia[] = [
  INSTALAR_O_RASTRO,
  INSTALAR_O_PLAYWRIGHT,
  {
    titulo: "Chame o robô",
    texto:
      "Rode o comando trocando o endereço pelo do site que você quer analisar. O Chrome (ou o Edge) abre sozinho nesse site.",
    comandos: [
      { sistema: "Linux", texto: "rastro gravar https://site.com.br --robo" },
      { sistema: "Windows", texto: "rastro gravar https://site.com.br --robo" },
    ],
    dica: "Em produção, não use um usuário administrador ou com acesso a dados sensíveis: um link comum pode aprovar, arquivar ou enviar algo. Nesse caso, escolha \"O Rastro grava\" e navegue você mesmo.",
    ilustracao: "robo",
  },
  {
    titulo: "Entre e aperte Enter",
    texto:
      "Se o site pede login, entre na janela que abriu. Depois, volte ao terminal e aperte `Enter`. Sem login, só aperte `Enter`.",
    ilustracao: "entrar",
  },
  {
    titulo: "Espere o robô",
    texto:
      "O robô visita os links do site, até 20 páginas ou 3 minutos, e mostra cada página no terminal. Ele não clica em botões, não envia formulários e não sai do site.",
    dica: "Quando ele parar, a janela continua aberta: visite outra página, se quiser, e feche a janela.",
    ilustracao: "robo-visita",
  },
  ABRIR_O_RELATORIO_GRAVADO,
];

export const PASSOS_POR_MODO: Record<ModoDeUso, PassoDoGuia[]> = {
  devtools: PASSOS_PELO_DEVTOOLS,
  gravar: PASSOS_COM_O_RASTRO_GRAVANDO,
  robo: PASSOS_COM_O_ROBO,
};

export const PROBLEMAS: Problema[] = [
  {
    sintoma: "A aba Rede está vazia",
    solucao: "O DevTools precisa estar aberto antes de a página carregar. Recarregue com `Ctrl + R`.",
    modos: ["devtools"],
  },
  {
    sintoma: "O relatório diz que nenhuma resposta trouxe conteúdo JavaScript",
    solucao: "O HAR foi gravado sem os scripts. Quase sempre é o filtro da aba Rede (como Fetch/XHR), que deixa os scripts fora do arquivo, ou o cache, que grava os scripts sem o conteúdo. Deixe o filtro em **Todos**, marque **Desativar cache**, recarregue e exporte o HAR de novo.",
    modos: ["devtools"],
  },
  {
    sintoma: "As checagens de cookie estão como não verificadas",
    solucao: "É o esperado com o HAR sanitized, que tira os cookies. As bibliotecas são analisadas do mesmo jeito.",
    modos: ["devtools"],
  },
  {
    sintoma: "\"o Playwright não está instalado\" ao gravar",
    solucao: "Rode o comando de instalação que o próprio erro mostra. Ou escolha \"Gravo no navegador\" no alto desta tela.",
    modos: GRAVANDO_PELO_RASTRO,
  },
  {
    sintoma: "\"nem o Google Chrome nem o Microsoft Edge foram encontrados\"",
    solucao: "Instale um dos dois. O Rastro usa o navegador do computador e não baixa outro.",
    modos: GRAVANDO_PELO_RASTRO,
  },
  {
    sintoma: "\"não foi possível abrir o navegador para gravar a visita\"",
    solucao: "Feche as janelas do Chrome ou do Edge que estiverem travadas e rode de novo. Se continuar, escolha \"Gravo no navegador\" no alto desta tela.",
    modos: GRAVANDO_PELO_RASTRO,
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

export const SEUS_DADOS: Item[] = [
  { texto: "O HAR e o relatório ficam na sua máquina, e o Rastro não acessa o site analisado.", modos: ["devtools"] },
  {
    texto: "A gravação e o relatório ficam na sua máquina. A gravação guarda a sessão do site (o login): não compartilhe o arquivo e apague quando não precisar mais. O relatório não traz a sessão.",
    modos: GRAVANDO_PELO_RASTRO,
  },
  { texto: "A IA recebe só trechos de scripts, o nome e a versão das bibliotecas e os dados dos avisos, com tokens, chaves e parâmetros de endereço tirados antes." },
  { texto: "O GitHub Advisory, o OSV e o registro do npm recebem só o nome e a versão das bibliotecas; o NVD, só o CVE." },
];
