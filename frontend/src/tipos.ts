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
}

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

export interface ChamadaIA {
  etapa: string;
  provedor: string;
  entrada: string;
  resposta: string | null;
  duracao_s: number;
  tokens: number | null;
  sucesso: boolean;
}

export interface ComESemIA {
  bibliotecas: [number, number];
  achados: [number, number];
}

export interface DadosDaIA {
  chamadas: ChamadaIA[];
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
}
