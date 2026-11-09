# Decisão 03: a IA identifica e explica, mas não decide

Requisitos: R03, R07, R11 e R21. Código: `rastro/identificacao/ia.py`, `rastro/explicacao/ia.py` e `rastro/ia/`.

## Contexto

O curso pede que a IA tenha papel real no produto. Mas o relatório vira task para um dev, e o auditor precisa defender cada linha diante do time. A IA pode errar: inventar uma versão, um pacote ou um CVE, ou dar respostas diferentes para a mesma pergunta.

Há duas coisas que regra fixa não faz bem:

- **Reconhecer biblioteca dentro de bundle**, sem nome de arquivo nem comentário de versão. No Juice Shop, o `@angular/core@22.2.2` só foi achado pela IA (spike T03).
- **Explicar a falha em linguagem simples** para quem não é de segurança, com um teste para verificar a correção.

## Decisão

| A IA faz | A IA não faz |
|---|---|
| Sugere bibliotecas e versões em bundles, citando o trecho | Calcula nota, prioridade ou ordem (R05.7) |
| Explica cada achado: o que é, impacto, como corrigir | Preenche CVE, GHSA, versão, CVSS, EPSS, link ou versão-alvo (R21.8) |
| Sugere um teste de verificação, marcado "sugerido pela IA: confira antes de usar" | Esconde achado ou decide o que entra no plano de ação |
| | Escreve o texto da task (é um modelo fixo, `acao/task.py`) |
| | Pesquisa na internet ou recebe cookies, senhas e tokens |

- **A IA sugere, a regra confirma.** Tudo o que ela devolve passa pelas travas antes de virar dado ([decisão 06](06-travas-contra-invencao.md)).
- **O relatório mostra o que a IA fez:** cada chamada com a entrada, a resposta, o tempo e os tokens, o que cada trava barrou e a comparação "só por assinatura × com a IA" (R11).
- A IA é configurável ([decisão 04](04-ia-por-cli.md)) e pode ser desligada ([decisão 08](08-analise-sem-ia.md)).

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Agente de IA que pesquisa, prioriza e escreve o relatório | Não é reproduzível nem explicável, e pode inventar CVE e versão. O auditor não teria como defender o resultado. |
| IA ajusta a prioridade pelo contexto do site | A nota deixaria de ser refeita à mão. Proibido por R05.7. |
| IA escreve a task inteira | O texto da task cita versão, GHSA e versão-alvo. Com modelo fixo, esses dados vêm só das fontes. |
| Sem IA | Perde as bibliotecas em bundles e a explicação simples, e o curso pede IA com papel real. Fica como opção, não como padrão. |
