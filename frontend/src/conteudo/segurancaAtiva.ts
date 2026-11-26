import type { CategoriaDoPentest } from "../relatorio/tiposDoRelatorio.ts";
import type { Veredito } from "../segurancaAtiva/agruparValidacoes.ts";

export interface DescricaoDaValidacao {
  nome: string;
  porque: string;
}

export const DESCRICAO_DA_VALIDACAO: Record<CategoriaDoPentest, DescricaoDaValidacao> = {
  csp: {
    nome: "Política de conteúdo (CSP)",
    porque: "Diz ao navegador de onde a página pode carregar scripts. Sem ela, um script injetado roda sem barreira.",
  },
  csp_diretiva: {
    nome: "Brechas na política de conteúdo",
    porque: "As opções unsafe-inline e unsafe-eval liberam justamente o tipo de script que a CSP deveria barrar.",
  },
  hsts: {
    nome: "HTTPS obrigatório (HSTS)",
    porque: "Faz o navegador usar sempre HTTPS. Sem isso, uma conexão numa rede insegura pode ser desviada.",
  },
  nosniff: {
    nome: "Tipo de arquivo travado (nosniff)",
    porque: "Impede o navegador de tratar como script um arquivo que não é script.",
  },
  frame: {
    nome: "Proteção contra moldura (frame)",
    porque: "Impede outro site de exibir esta página escondida dentro dele para enganar cliques.",
  },
  referrer_policy: {
    nome: "Endereço enviado a outros sites",
    porque: "Controla quanto do endereço da página vai junto quando a pessoa clica num link para fora.",
  },
  permissions_policy: {
    nome: "Recursos do navegador (câmera, local…)",
    porque: "Desliga recursos que a página não usa. É uma boa prática, não uma falha grave.",
  },
  server_version: {
    nome: "Versão do servidor à mostra",
    porque: "Mostrar a versão ajuda quem procura falhas conhecidas daquela versão.",
  },
  cors: {
    nome: "Leitura por outros sites (CORS)",
    porque: "Define quais outros sites podem ler as respostas deste. Liberado demais, outro site lê dados de quem está logado.",
  },
  cookie: {
    nome: "Proteção dos cookies",
    porque: "HttpOnly, Secure e SameSite evitam que o cookie seja lido por scripts, enviado sem HTTPS ou usado por outro site.",
  },
  execucao: {
    nome: "Endereços sem resposta",
    porque: "O site não respondeu a tempo, então nada pôde ser conferido nesses endereços.",
  },
};

export const FORA_DO_ESCOPO: string[] = [
  "Login e sessão",
  "Permissões entre usuários",
  "Injeção de código (SQL, XSS)",
  "Regras de negócio",
];

export interface GrupoDoPentest {
  veredito: Veredito;
  titulo: string;
  legenda: string;
}

export const GRUPOS_DO_PENTEST: GrupoDoPentest[] = [
  { veredito: "corrigir", titulo: "A corrigir", legenda: "falhou em pelo menos um endereço" },
  { veredito: "em_ordem", titulo: "Em ordem", legenda: "passou em todos os endereços que responderam" },
  { veredito: "sem_resposta", titulo: "Não conferido", legenda: "não deu para conferir nesta execução" },
];
