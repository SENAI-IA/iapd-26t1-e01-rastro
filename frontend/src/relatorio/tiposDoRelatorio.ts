export type Prioridade = "alta" | "media" | "baixa" | "a avaliar";
export type Severidade = "alta" | "media" | "baixa";
export type SituacaoDaChecagem = "falhou" | "passou" | "nao_verificada";
export type MetodoDeIdentificacao = "assinatura" | "ia";
export type SituacaoDaBiblioteca = "confirmada" | "a_confirmar";

export interface Limitacao {
  id: string;
  texto: string;
}

export interface DadosDaAnalise {
  har: string;
  site: string | null;
  data: string;
  ia: string | null;
  limitacoes: Limitacao[];
  continua_igual: string | null;
  duracao_s: number;
}

export interface Resumo {
  nota_maxima: number | null;
  acoes: number;
  acoes_por_prioridade: Record<Prioridade, number>;
  bibliotecas: number;
  bibliotecas_vulneraveis: number;
  bibliotecas_a_confirmar: number;
  bibliotecas_nao_consultadas: number;
  achados: number;
  checagens_com_falha: number;
  checagens_nao_verificadas: number;
  encontradas_so_pela_ia: number | null;
}

export interface Evidencia {
  indice_requisicao: number;
  url: string;
  trecho: string | null;
}

export interface Explicacao {
  o_que_e: string;
  impacto: string;
  como_corrigir: string;
  teste_verificacao: string;
  gerada_por_ia: boolean;
}

export interface Biblioteca {
  id: string;
  pacote: string;
  versao: string;
  metodo: MetodoDeIdentificacao;
  situacao: SituacaoDaBiblioteca;
  conferida_no_npm: boolean | null;
  travas_que_falharam: string[];
  evidencias: Evidencia[];
  nota: number | null;
  prioridade: Prioridade | null;
  achados: string[];
  motivo_nao_consultada: string | null;
  explicacao: Explicacao | null;
}

export interface Aviso {
  fontes: string[];
  apelidos: string[];
  ghsa: string;
  cve: string | null;
  resumo: string;
  cvss: number | null;
  percentil_epss: number | null;
  versoes_afetadas: string;
  versao_corrigida: string | null;
  link: string;
  origem_dos_campos: FonteDeCadaCampo;
}

export type CampoComOrigem =
  | "cve"
  | "resumo"
  | "cvss"
  | "percentil_epss"
  | "versoes_afetadas"
  | "versao_corrigida"
  | "link";

export type FonteDeCadaCampo = Partial<Record<CampoComOrigem, string>>;

export interface Nota {
  valor: number | null;
  prioridade: Prioridade;
  conta: string;
  sem_epss: boolean;
}

export interface Achado {
  biblioteca: string;
  aviso: Aviso;
  nota: Nota;
}

export interface Checagem {
  id: string;
  titulo: string;
  situacao: SituacaoDaChecagem;
  severidade: Severidade;
  quem_resolve: string;
  evidencia: Evidencia | null;
  detalhe: string;
}

export interface Acao {
  id: string;
  prioridade: Prioridade;
  nota: number | null;
  o_que_fazer: string;
  porque: string;
  impacto: string;
  quem_resolve: string;
  refs: string[];
  teste_verificacao: string | null;
  texto_task: string;
}

export interface TravaAcionada {
  trava: string;
  alvo: string;
  motivo: string;
}

export interface ChamadaDaIA {
  etapa: string;
  provedor: string;
  entrada: string;
  resposta: string;
  duracao_s: number;
  tokens: number | null;
  sucesso: boolean;
}

export interface Contagem {
  so_por_assinatura: number;
  com_ia: number;
}

export interface ComESemIA {
  bibliotecas: Contagem;
  achados: Contagem;
}

export interface DadosDaIA {
  chamadas: ChamadaDaIA[];
  travas_acionadas: TravaAcionada[];
  com_e_sem_ia: ComESemIA | null;
  tokens_total: number | null;
}

export interface Relatorio {
  versao_formato: number;
  analise: DadosDaAnalise;
  resumo: Resumo;
  bibliotecas: Biblioteca[];
  a_confirmar: Biblioteca[];
  achados: Achado[];
  checagens: Checagem[];
  plano_de_acao: Acao[];
  ia: DadosDaIA;
  visita?: PassoDaVisita[];
  pentest?: ResultadoDoPentest | null;
}

export type Camada = "pagina" | "script" | "estilo" | "dados" | "midia";

export interface PassoDaVisita {
  indice_requisicao: number;
  url: string;
  camada: Camada;
  inicio_ms: number;
  duracao_ms: number;
  bibliotecas: string[];
  prioridade: Prioridade | null;
}

export type CategoriaDoPentest =
  | "csp"
  | "hsts"
  | "nosniff"
  | "frame"
  | "referrer_policy"
  | "permissions_policy"
  | "server_version"
  | "cors"
  | "cookie"
  | "csp_diretiva"
  | "execucao";
export type SituacaoDoPentest = "falhou" | "passou" | "nao_verificada";
export type MetodoHttpSemEfeito = "GET" | "HEAD" | "OPTIONS";

export interface RequisicaoDoPentest {
  indice_har: number;
  metodo: MetodoHttpSemEfeito;
  status: number | null;
  url: string;
  erro: string | null;
}

export interface ValidacaoDoPentest {
  id: string;
  categoria: CategoriaDoPentest;
  titulo: string;
  situacao: SituacaoDoPentest;
  detalhe: string;
  referencia: string | null;
  requisicao: RequisicaoDoPentest;
}

export interface ResumoDoPentest {
  requisicoes_enviadas: number;
  requisicoes_ignoradas: number;
  falharam: number;
  passaram: number;
  nao_verificadas: number;
}

export interface ResultadoDoPentest {
  versao_formato: number;
  origem: "rastro";
  modo: "ativo";
  executado_em: string;
  har: string;
  har_sha256: string;
  site: string;
  limite_de_requisicoes: number;
  requisicoes_enviadas: number;
  validacoes: ValidacaoDoPentest[];
  resumo: ResumoDoPentest;
}
