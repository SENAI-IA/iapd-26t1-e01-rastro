# Decisão 09: HAR sanitized como recomendado

Requisitos: R06.7, R16.4 e R16.5. Código: `rastro/har/leitor.py` e `rastro/configuracao/checagens.py`.

## Contexto

O DevTools do Chrome exporta o HAR de dois jeitos: **sanitized**, sem cookies e cabeçalhos de autenticação, e **completo** (*with sensitive data*). O completo traz o cookie de sessão, o `Authorization` e outros segredos do sistema auditado, que passam a ficar na máquina de quem audita e podem acabar num repositório ou num anexo.

O Rastro precisa do conteúdo dos scripts e dos cabeçalhos de resposta, que vêm nos dois. Os cookies só servem para três checagens: C06 (HttpOnly), C07 (Secure) e C08 (SameSite).

## Decisão

- **O Rastro aceita os dois e recomenda o sanitized.** O completo só acrescenta as checagens C06 a C08.
- **Sem cookies no HAR, C06 a C08 ficam "não verificada"**, nunca "passou", com o detalhe dizendo que o HAR completo inclui essas checagens (R06.7).
- **Mesmo com o HAR completo, nenhum segredo sai do Rastro:** o leitor guarda só o nome e os atributos de cada cookie, nunca o valor, e descarta os cabeçalhos do pedido. A IA não recebe cookies, cabeçalhos nem corpos (R16.3), e o relatório não traz valor de cookie nem token (R16.4).
- **Na avaliação e no repositório, só HAR sanitized.** O `.gitignore` ignora `*.har`, menos os de `avaliacao/` e `tests/`. Os HARs de `avaliacao/` foram gravados pelo Playwright e sanitizados com a mesma regra do Chrome: sem `Cookie`, `Set-Cookie`, `Authorization` e `Proxy-Authorization`, e com as listas de cookies vazias (`avaliacao/README.md`).

**Em aberto:** comparar à mão o HAR sanitized e o completo exportados do Chrome na mesma navegação (pendente da T04, `avaliacao/README.md`). Se o sanitized do Chrome tirar mais coisas, os HARs da avaliação são gerados de novo com a mesma regra.

**Limite conhecido:** cookie criado por JavaScript não tem `Set-Cookie`, então fica de fora das checagens mesmo no HAR completo. É o caso do Juice Shop (spike T03).

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Exigir o HAR completo | Leva segredos para a máquina e para o repositório por causa de três checagens de severidade média e baixa. |
| Recusar o HAR completo | Quem só tem o completo ficaria sem análise, e o Rastro já não guarda nenhum valor sensível. |
| O Rastro limpar e regravar o HAR | Gravaria um arquivo além do relatório (R17.1), e o HAR original com os segredos continuaria na máquina. |
| Buscar os cookies no próprio site | Seria uma requisição ao site analisado. O Rastro só faz análise passiva (R16.1). |
