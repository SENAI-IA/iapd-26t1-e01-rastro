# Decisão 06: travas contra invenção. A IA sugere, a regra confirma

Requisito: R21. Código: `rastro/travas/` e `rastro/fontes/registro_npm.py`.

## Contexto

A IA pode inventar uma versão, citar um pacote vizinho ou um CVE que não existe. No relatório, esse erro vira uma task errada para o dev e tira a confiança no resto. O auditor precisa mostrar, para cada dado, de onde ele veio e quem o conferiu.

No spike T03, a IA leu o trecho `` `FA "5.15.4"` `` do Juice Shop e sugeriu `@fortawesome/fontawesome-free@5.15.4`. O pacote existe, a versão existe e está no trecho, mas o bundle traz outro pacote da família (`docs/spike/har-e-bundles.md`). Conferir só o nome e a versão não basta.

## Decisão

Toda saída da IA passa por **travas determinísticas**, funções puras com nome que diz o que conferem:

| # | Trava | Se falhar |
|---|---|---|
| 1 | Formato fechado: a resposta é exatamente o JSON pedido? | descarta a resposta inteira |
| 2 | Trecho real: o trecho citado foi mesmo enviado à IA? | "a confirmar" |
| 3 | Ancoragem: a versão aparece escrita no trecho? | "a confirmar" |
| 4 | Pacote existe: `pacote@versão` foi publicado no npm? | "a confirmar" |
| 5 | Código confere: as strings do trecho estão no código publicado daquela versão? | "a confirmar" |
| 6 | Faixa conferida: a versão está na faixa afetada do aviso? | descarta o aviso |
| 7 | Explicação sem fato novo: só cita CVE, GHSA, versões e números da entrada? | usa o resumo do aviso |

- **Biblioteca "a confirmar"** não entra na nota nem no plano de ação, mas também não some: fica numa lista própria, com a trava que falhou e como confirmar à mão.
- **Tudo o que uma trava barra fica registrado** no painel da IA: qual trava, o que barrou e por quê (R21.10).
- As travas 4 e 6 valem também para a biblioteca achada por assinatura, com ou sem IA.
- **Registro do npm, só leitura.** A trava 4 lê os metadados da versão. A trava 5 baixa o `.tgz` do próprio `registry.npmjs.org`, confere a integridade (`sha512`) e lê os arquivos `.js` **em memória**, com limites de tamanho (10 MB baixados, 50 MB abertos). Nada é instalado, extraído em disco ou executado.
- Sem resposta do npm, a biblioteca por assinatura segue com o selo "não conferida no npm", e a da IA vai para "a confirmar" (R21.9). O que não foi conferido não passa.

**Limite conhecido:** um pacote que traz por dentro o código de outro, na mesma versão, passa pela trava 5, porque o código é mesmo dele. Por isso a biblioteca da IA aparece sempre com o método "ia" e o trecho como evidência.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Confiar na IA, com o aviso "confira" | Empurra a conferência para o auditor, que não é especialista e não teria como fazê-la. |
| Uma segunda IA revisa a primeira | Mesma fonte de erro, sem resultado repetível. Não dá para explicar na banca por que algo passou. |
| `npm install` do pacote para comparar o código | Roda scripts de instalação de terceiros, grava em disco e exige Node. Vai contra R17. |
| Comparar o trecho com espaços normalizados | No spike, nunca passou: o minificador renomeia variáveis e troca as aspas. A trava 5 compara o valor das strings. |
| Aceitar "a versão aparece no pacote" | No spike, deixou passar invenção: só a versão não prova o pacote. |
| Aceitar só o que vem por assinatura | Perde o que só a IA acha em bundles, como o `@angular/core` do Juice Shop. |
