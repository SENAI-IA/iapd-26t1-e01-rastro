# Kanban: Rastro MVP

Quadro de controle das tasks. **O que** cada task faz está no `tasks.md`; **em que pé** ela está, aqui.

## Regras

- **Um cartão = uma task do `tasks.md`.** Mesmo número, mesmo título.
- **Mover é recortar a linha** de uma coluna e colar na outra. O diff do Git mostra a mudança de estado.
- **Ao começar:** move para "Em andamento".
- **No commit da task** (direto no `main`): move para "Em revisão", marca `[x]` no `tasks.md` e acrescenta o commit e a data: `· commit 3f2a9c1 · 18/11`.
- **Ao aprovar:** move para "Feito" e marca `[x]` aqui, no próximo commit que for feito. Ajuste pedido na revisão vira commit `fix(...) (Tnn)`, anotado no cartão: `· ajuste 7b1e044`.
- **Bloqueou?** O cartão fica onde está e ganha `· bloqueada: <motivo>`. Bloqueio com mais de um dia vai para a conversa do grupo.
- **Uma task "Em andamento" por vez** (tudo vai direto no `main`) e **no máximo 3 "Em revisão"**. Passou disso, a revisão anda antes de começar outra.
- Cartão que não é task (ajuste de documento, correção pequena) usa `Sxx` e segue as mesmas colunas.

## Em andamento

_(vazio)_

## Em revisão

- [ ] **T01** Validar o GitHub Advisory e o EPSS · fase 0 · revisão @cristiano.albino · commit f8c8fe6 · 06/11
- [ ] **T02** Validar as CLIs de IA sem interação · fase 0 · revisão @luiz.pagliari · commit 36ca444 · 06/11 · Windows conferido na T42
- [ ] **T03** Validar o HAR real e o bundle do Juice Shop · fase 0 · revisão @ali.santos · commit df8697a · 06/11 · HAR do Chrome conferido na T04
- [ ] **T04** Montar a avaliação · fase 0 · revisão @geison.santos · commit 059244b · 06/11 · pendente: exportar do Chrome o HAR sanitized e o completo e conferir (`avaliacao/README.md`)
- [ ] **T05** Criar o esqueleto Python · fase 0 · revisão @ali.santos · commit 6a52bb3 · 06/11 · Windows conferido na T42
- [ ] **T06** Documentar a verificação local · fase 0 · revisão @luiz.pagliari · commit c39f326 · 06/11 · Windows conferido na T42 (`docs/cobertura/windows.md`)
- [ ] **T07** Escrever a skill `rastro-nova-regra` · fase 0 · revisão @luiz.pagliari · commit 32e1fb3 · 06/11 · aceite só em T10 e T19 (uso real da skill)
- [ ] **T08** Ler e validar o HAR · fase 1 · revisão @ali.santos · commit e4e8a26 · 06/11
- [ ] **T09** Descobrir o site analisado · fase 1 · revisão @ali.santos · commit aa540f5 · 06/11
- [ ] **T10** Identificar bibliotecas pelo nome do arquivo · fase 1 · revisão @ali.santos · commit 10dfc8e · 06/11
- [ ] **T11** Identificar bibliotecas pelo comentário de versão · fase 1 · revisão @ali.santos · commit 42ae31a · 09/11
- [ ] **T12** Consultar o GitHub Advisory · fase 1 · revisão @cristiano.albino · commit 164761a · 09/11
- [ ] **T13** Conferir a faixa de versão afetada · fase 1 · revisão @cristiano.albino · commit 1fac299 · 09/11
- [ ] **T14** Conferir no npm se o pacote existe · fase 1 · revisão @cristiano.albino · commit 04a96e8 · 09/11
- [ ] **T15** Travar a resposta da IA: formato e ancoragem · fase 1 · revisão @cristiano.albino · commit 0169a38 · 09/11
- [ ] **T16** Barrar explicação com fato novo · fase 1 · revisão @cristiano.albino · commit 8c9fdd2 · 09/11
- [ ] **T17** Calcular a nota de risco · fase 1 · revisão @geison.santos · commit 2da7b15 · 09/11
- [ ] **T18** Classificar a prioridade e ordenar · fase 1 · revisão @geison.santos · commit 11d7443 · 09/11
- [ ] **T19** Checar os cabeçalhos de segurança · fase 1 · revisão @geison.santos · commit f6eb8cf · 09/11
- [ ] **T20** Checar os cookies · fase 1 · revisão @geison.santos · commit d914873 · 09/11
- [ ] **T21** Montar o plano de ação · fase 1 · revisão @geison.santos · commit 0a77e09 · 09/11
- [ ] **T22** Gerar o texto da task · fase 1 · revisão @geison.santos · commit 461d80f · 09/11
- [ ] **T23** Gravar o relatório JSON e ligar o fluxo sem IA · fase 1 · revisão @geison.santos · commit bcb9cae · 09/11
- [ ] **T24** Criar o projeto do frontend · fase 2 · revisão @halan.bacca · commit 9e54984 · 09/11
- [ ] **T25** Embutir o JSON no HTML · fase 2 · revisão @halan.bacca · commit 358fbd6 · 09/11
- [ ] **T26** Mostrar os indicadores e o plano de ação · fase 2 · revisão @halan.bacca · commit 53a5ed8 · 09/11
- [ ] **T27** Mostrar o aviso de análise sem IA · fase 2 · revisão @halan.bacca · commit bde4ec8 · 09/11
- [ ] **T28** Mostrar bibliotecas, falhas e checagens · fase 2 · revisão @halan.bacca · commit 25a07c8 · 09/11
- [ ] **T29** Mostrar a origem de cada dado · fase 2 · revisão @halan.bacca · commit a35c8dd · 09/11
- [ ] **T30** Mostrar o glossário · fase 2 · revisão @halan.bacca · 09/11
- [ ] **S01** Atualizar PRD, pitch e steering com as decisões da spec e regerar os PDFs · antes da fase 0 · revisão: todos, junto com a spec (S02)

## A fazer

### Fase 0. Preparar

_(vazio)_

### Fase 1. Núcleo determinístico

_(vazio)_

### Fase 2. Relatório HTML

- [ ] **T31** Abrir e copiar a task · fase 2 · 23–28/11 · revisão @halan.bacca
- [ ] **T32** Ler uma zona por vez (modo foco) · fase 2 · 23–28/11 · revisão @halan.bacca

### Fase 3. IA

- [ ] **T33** Criar o cliente de IA e a escolha do provedor · fase 3 · 30/11–04/12 · revisão @luiz.pagliari
- [ ] **T34** Tirar dados sensíveis do que vai para a IA · fase 3 · 30/11–04/12 · revisão @cristiano.albino
- [ ] **T35** Chamar o Claude pela CLI · fase 3 · 30/11–04/12 · revisão @luiz.pagliari
- [ ] **T36** Chamar o Codex pela CLI · fase 3 · 30/11–04/12 · revisão @luiz.pagliari
- [ ] **T37** Chamar o Kiro pela CLI · fase 3 · 30/11–04/12 · revisão @luiz.pagliari
- [ ] **T38** Explicar cada achado com IA · fase 3 · 30/11–04/12 · revisão @luiz.pagliari
- [ ] **T39** Mostrar onde a IA entrou · fase 3 · 30/11–04/12 · revisão @luiz.pagliari
- [ ] **T40** Conferir o trecho no código publicado · fase 3 · 30/11–04/12 · revisão @ali.santos
- [ ] **T41** Identificar bibliotecas em bundles com IA · fase 3 · 30/11–04/12 · revisão @ali.santos · prazo limite 04/12

### Fase 4. Entregar

- [ ] **T42** Instalar do zero no Windows e no Linux · fase 4 · 04–08/12 · revisão @ali.santos
- [ ] **T43** Escrever o README de uso · fase 4 · 04–08/12 · revisão @cristiano.albino
- [ ] **T44** Publicar o relatório de cobertura · fase 4 · 04–08/12 · revisão @geison.santos
- [ ] **T45** Registrar as decisões · fase 4 · 04–08/12 · revisão @cristiano.albino
- [ ] **T46** Medir com e sem IA · fase 4 · 04–08/12 · revisão @luiz.pagliari
- [ ] **T47** Gravar a apresentação e o demo · fase 4 · 04–08/12 · revisão @halan.bacca
- [ ] **T48** Preparar a versão final · fase 4 · 04–08/12 · revisão @luiz.pagliari

### Extensão: OSV e NVD (só se houver tempo, até 02/12)

- [ ] **T49** Consultar o OSV · extensão · até 02/12 · revisão @cristiano.albino
- [ ] **T50** Completar o CVSS pelo NVD · extensão · até 02/12 · revisão @ali.santos
- [ ] **T51** Juntar avisos de fontes diferentes · extensão · até 02/12 · revisão @geison.santos

## Feito

- [x] **S02** Commitar a spec no `main` (ponto de partida 61d939e) · 06/11
- [x] **S03** Coletar os e-mails do Git dos revisores para a linha `Co-authored-by` · antes da fase 1 · feito 06/11
