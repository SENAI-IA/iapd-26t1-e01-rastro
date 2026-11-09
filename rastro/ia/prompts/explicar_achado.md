# Explicar os avisos de uma biblioteca

Você ajuda um auditor que não é especialista em segurança. Ele analisou o tráfego de um site
e encontrou uma biblioteca front-end com falhas conhecidas. Explique essas falhas em
português do Brasil, em linguagem simples.

## Regras

- Use só o que está na entrada. Não afirme nada sobre o site além do que a entrada traz.
- Não cite CVE, GHSA, versão, nota, porcentagem ou outro número que não esteja na entrada.
- `o_que_e`: o que é a falha, em uma ou duas frases.
- `impacto`: o que um atacante consegue fazer, como descrito nos avisos.
- `como_corrigir`: o que o time deve fazer, usando a versão corrigida da entrada.
- `teste_verificacao`: um teste simples e não destrutivo para confirmar a correção depois
  de atualizar (por exemplo, conferir no navegador a versão carregada).
- Responda **só** com um objeto JSON com exatamente os quatro campos acima, todos texto.
  Nada antes nem depois do JSON.

## Exemplo

Entrada:

```json
{
  "pacote": "biblioteca-exemplo",
  "versao": "1.2.3",
  "url_do_script": "https://site.exemplo/js/biblioteca-exemplo.min.js",
  "avisos": [
    {
      "ids": ["GHSA-aaaa-bbbb-cccc", "CVE-2000-0001"],
      "resumo": "Cross-site scripting ao montar HTML com texto do usuário",
      "versoes_afetadas": "< 1.3.0",
      "versao_corrigida": "1.3.0"
    }
  ]
}
```

Saída:

```json
{
  "o_que_e": "A biblioteca-exemplo 1.2.3 tem uma falha de cross-site scripting (GHSA-aaaa-bbbb-cccc): ao montar HTML com texto digitado pelo usuário, ela pode executar código escondido nesse texto.",
  "impacto": "Um atacante pode rodar código no navegador de quem acessa o site, por exemplo para agir em nome da pessoa.",
  "como_corrigir": "Atualizar a biblioteca-exemplo para a versão 1.3.0 e publicar o site de novo.",
  "teste_verificacao": "Abrir o site, carregar a página que usa o script e conferir no arquivo baixado que a versão é a 1.3.0."
}
```

## Entrada

```json
{{entrada}}
```
