export const glossario = {
  HAR: "Arquivo que o navegador gera com tudo o que a página baixou: endereços, cabeçalhos e o conteúdo dos scripts. É a gravação da navegação.",
  CVSS: "Nota de 0 a 10 para o estrago que uma falha causa se for explorada. Mede a gravidade, não a chance de acontecer.",
  EPSS: "Chance de uma falha ser explorada na prática nos próximos 30 dias. Percentil 97 quer dizer: mais provável que 97% das falhas conhecidas.",
  Bundle:
    "Arquivo único em que o build junta o código do site e das bibliotecas, quase sempre minificado. Esconde quais bibliotecas e versões estão ali.",
  Assinatura:
    "Padrão conhecido que identifica uma biblioteca, como o nome do arquivo ou o comentário de versão no topo dele.",
  npm: "Registro público dos pacotes de JavaScript. O Rastro só lê o registro, para conferir que o pacote e a versão existem.",
  Crédito:
    "Medida de uso que o Kiro cobra por chamada, no lugar dos tokens. O Rastro mostra o número que o Kiro informa, sem converter.",
  Token:
    "Pedaço de texto que a IA lê ou escreve, mais ou menos uma sílaba. É a medida de uso que os provedores cobram.",
  Trava:
    "Regra fixa que confere um dado antes de ele entrar no relatório: o que a IA devolveu, o pacote no npm, a faixa de versão afetada. O que não passa é barrado e fica registrado.",
  Pentest:
    "Avaliação de segurança com escopo definido e autorização. No Rastro, cobre a configuração de segurança das respostas do site, sem ataques e fora da nota.",
  WSTG:
    "Guia aberto da OWASP com os testes de segurança de sites. O código, como WSTG-CONF-12, diz qual teste do guia foi feito.",
} as const satisfies Record<string, string>;

export type NomeDoTermo = keyof typeof glossario;
