# Kanban: Rastro

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

- [ ] **T46** Medir com e sem IA · fase 4 · 04–08/12 · revisão @luiz.pagliari · parcial 09/11 · commit 08ed731 · pendente: tempo de triagem manual (medir com uma pessoa) · Codex fora da medição (chave de API removida, sem outra no grupo)

## Em revisão

- [ ] **T01** Validar o GitHub Advisory e o EPSS · fase 0 · revisão @cristiano.albino · commit eb266c5 · 06/11
- [ ] **T02** Validar as CLIs de IA sem interação · fase 0 · revisão @luiz.pagliari · commit fb86486 · 06/11 · Windows pendente: fica para a T42
- [ ] **T03** Validar o HAR real e o bundle do Juice Shop · fase 0 · revisão @ali.santos · commit aa551a5 · 06/11 · HAR do Chrome conferido na T04
- [ ] **T04** Montar a avaliação · fase 0 · revisão @geison.santos · commit afc4586 · 06/11 · pendente: exportar do Chrome o HAR sanitized e o completo e conferir (`avaliacao/README.md`)
- [ ] **T05** Criar o esqueleto Python · fase 0 · revisão @ali.santos · commit b8a8a2e · 06/11 · Windows pendente: fica para a T42
- [ ] **T06** Documentar a verificação local · fase 0 · revisão @luiz.pagliari · commit 1ae1674 · 06/11 · Windows pendente: fica para a T42 (`docs/cobertura/windows.md` ainda não existe)
- [ ] **T07** Escrever a skill `rastro-nova-regra` · fase 0 · revisão @luiz.pagliari · commit 3536553 · 06/11 · aceite só em T10 e T19 (uso real da skill)
- [ ] **T08** Ler e validar o HAR · fase 1 · revisão @ali.santos · commit 6a82d89 · 06/11
- [ ] **T09** Descobrir o site analisado · fase 1 · revisão @ali.santos · commit 9d61261 · 06/11
- [ ] **T10** Identificar bibliotecas pelo nome do arquivo · fase 1 · revisão @ali.santos · commit 7a5c225 · 06/11
- [ ] **T11** Identificar bibliotecas pelo comentário de versão · fase 1 · revisão @ali.santos · commit f73fae7 · 09/11
- [ ] **T12** Consultar o GitHub Advisory · fase 1 · revisão @cristiano.albino · commit 2acdb57 · 09/11
- [ ] **T13** Conferir a faixa de versão afetada · fase 1 · revisão @cristiano.albino · commit 9e06383 · 09/11
- [ ] **T14** Conferir no npm se o pacote existe · fase 1 · revisão @cristiano.albino · commit 75127db · 09/11
- [ ] **T15** Travar a resposta da IA: formato e ancoragem · fase 1 · revisão @cristiano.albino · commit 0f14ced · 09/11
- [ ] **T16** Barrar explicação com fato novo · fase 1 · revisão @cristiano.albino · commit 6e0b5fa · 09/11
- [ ] **T17** Calcular a nota de risco · fase 1 · revisão @geison.santos · commit c9c5cdb · 09/11
- [ ] **T18** Classificar a prioridade e ordenar · fase 1 · revisão @geison.santos · commit 41ee35f · 09/11
- [ ] **T19** Checar os cabeçalhos de segurança · fase 1 · revisão @geison.santos · commit 4ae4909 · 09/11
- [ ] **T20** Checar os cookies · fase 1 · revisão @geison.santos · commit 9556f02 · 09/11
- [ ] **T21** Montar o plano de ação · fase 1 · revisão @geison.santos · commit 7262e87 · 09/11
- [ ] **T22** Gerar o texto da task · fase 1 · revisão @geison.santos · commit dd19b71 · 09/11
- [ ] **T23** Gravar o relatório JSON e ligar o fluxo sem IA · fase 1 · revisão @geison.santos · commit 1013f10 · 09/11
- [ ] **T24** Criar o projeto do frontend · fase 2 · revisão @halan.bacca · commit befee53 · 09/11
- [ ] **T25** Embutir o JSON no HTML · fase 2 · revisão @halan.bacca · commit e351057 · 09/11
- [ ] **T26** Mostrar os indicadores e o plano de ação · fase 2 · revisão @halan.bacca · commit abd7262 · 09/11
- [ ] **T27** Mostrar o aviso de análise sem IA · fase 2 · revisão @halan.bacca · commit 0d887b7 · 09/11
- [ ] **T28** Mostrar bibliotecas, falhas e checagens · fase 2 · revisão @halan.bacca · commit 93d319b · 09/11
- [ ] **T29** Mostrar a origem de cada dado · fase 2 · revisão @halan.bacca · commit b777de7 · 09/11
- [ ] **T30** Mostrar o glossário · fase 2 · revisão @halan.bacca · commit b55acf7 · 09/11
- [ ] **T31** Abrir e copiar a task · fase 2 · revisão @halan.bacca · commit 8df7726 · 09/11
- [ ] **T32** Ler uma zona por vez (modo foco) · fase 2 · revisão @halan.bacca · commit ee4b38c · 09/11
- [ ] **T33** Criar o cliente de IA e a escolha do provedor · fase 3 · revisão @luiz.pagliari · commit dc557b5 · 09/11
- [ ] **T34** Tirar dados sensíveis do que vai para a IA · fase 3 · revisão @cristiano.albino · commit 3fceb7c · 09/11
- [ ] **T35** Chamar o Claude pela CLI · fase 3 · revisão @luiz.pagliari · commit 6417860 · 09/11
- [ ] **T36** Chamar o Codex pela CLI · fase 3 · revisão @luiz.pagliari · commit dd5da6e · 09/11
- [ ] **T37** Chamar o Kiro pela CLI · fase 3 · revisão @luiz.pagliari · commit 719a4a2 · 09/11
- [ ] **T38** Explicar cada achado com IA · fase 3 · revisão @luiz.pagliari · commit fdcf1e9 · 09/11
- [ ] **T39** Mostrar onde a IA entrou · fase 3 · revisão @luiz.pagliari · commit 4ac1198 · 09/11
- [ ] **T40** Conferir o trecho no código publicado · fase 3 · revisão @ali.santos · commit 04f17d6 · 09/11
- [ ] **T41** Identificar bibliotecas em bundles com IA · fase 3 · revisão @ali.santos · commit 4b9ab19 · 09/11
- [ ] **T52** Ligar a IA na linha de comando · fase 3 · revisão @luiz.pagliari · 09/11 · commit de51d5d
- [ ] **T49** Consultar o OSV · extensão · revisão @cristiano.albino · 09/11 · commit 9553f06
- [ ] **T50** Completar o CVSS pelo NVD · extensão · revisão @ali.santos · 09/11 · commit 05140ed
- [ ] **T51** Juntar avisos de fontes diferentes · extensão · revisão @geison.santos · 09/11 · commit a3521bb
- [ ] **T44** Publicar o relatório de cobertura · fase 4 · 04–08/12 · revisão @geison.santos · 09/11 · commit 4b6186f
- [ ] **T45** Registrar as decisões · fase 4 · 04–08/12 · revisão @cristiano.albino · 09/11 · commit d93d4b4
- [ ] **T43** Escrever o README de uso · fase 4 · 04–08/12 · revisão @cristiano.albino · 09/11 · commit 7f2d2af
- [ ] **T54** Rever a visita num radar · fase 2 · revisão @halan.bacca · 09/11 · spec da42b94 · commit 9b73418
- [ ] **T55** Ensinar a usar o relatório: tour guiado e Como usar · fase 2 · revisão @halan.bacca · 10/11
- [ ] **T56** Abrir o Como usar pela linha de comando · fase 2 · revisão @luiz.pagliari · 10/11 · spec 7ed91fe
- [ ] **T57** Rodar o Rastro de qualquer pasta · fase 2 · revisão @luiz.pagliari · 11/11
- [ ] **S01** Atualizar PRD, pitch e steering com as decisões da spec e regerar os PDFs · antes da fase 0 · revisão: todos, junto com a spec (S02)
- [ ] **S04** Alinhar a spec com a implementação: hashes do kanban, OSV e NVD entregues, design conferido com o código, sem "MVP" e pasta `specs/rastro` · revisão: todos · 10/11
- [ ] **T58** Registrar os spikes da gravação com Playwright · extensão · revisão a definir · 13/11
- [ ] **T59** Especificar a gravação da visita · extensão · revisão a definir · 13/11 · pendente: PRD e pitch (só em PDF)
- [ ] **T60** Gravar a visita à mão com `rastro gravar` · extensão · revisão a definir · 13/11 · pendente: fechar a janela e Windows (T42)
- [ ] **T61** Avisar sobre a sessão gravada no HAR · extensão · revisão a definir · 13/11
- [ ] **T62** Navegar sozinho com travas · extensão · revisão a definir · 13/11
- [ ] **T63** Combinar o robô com a navegação da pessoa · extensão · revisão a definir · 13/11
- [ ] **T64** Ensinar a gravar a visita · extensão · revisão a definir · 13/11 · pendente: Windows (T42)
- [ ] **T66** Instalar o Rastro com um comando só · fora das fases · revisão a definir · 24/11
- [ ] **T66** Criar a sonda HTTP segura das validações ativas · extensão segurança ativa · revisão @ali.santos · rebase
- [ ] **T67** Selecionar alvos e validar respostas ativas · extensão segurança ativa · revisão @cristiano.albino · rebase
- [ ] **T68** Gravar as validações de segurança ativas · extensão segurança ativa · revisão @geison.santos · rebase
- [ ] **T69** Levar as validações ativas ao JSON do relatório · extensão segurança ativa · revisão @geison.santos · rebase
- [ ] **T70** Mostrar a aba Segurança ativa no relatório · extensão segurança ativa · revisão @halan.bacca · rebase
- [ ] **T71** Situar a segurança ativa no guia OWASP WSTG · extensão segurança ativa · revisão @luiz.pagliari · 25/11
- [ ] **T72** Registrar a rodada de legibilidade e o diagrama da arquitetura · rodada de legibilidade · revisão @cristiano.albino · 25/11
- [ ] **T73** Dividir a linha de comando por comando · rodada de legibilidade · revisão @luiz.pagliari · 25/11
- [ ] **T74** Corrigir a direção das dependências entre camadas · rodada de legibilidade · revisão @geison.santos · 25/11
- [ ] **T75** Dar nome único e claro aos arquivos · rodada de legibilidade · revisão @ali.santos · 25/11
- [ ] **T76** Dividir a montagem do relatório JSON · rodada de legibilidade · revisão @geison.santos · 25/11
- [ ] **T77** Quebrar as validações ativas em uma função por validação · rodada de legibilidade · revisão @ali.santos · 25/11
- [ ] **T78** Juntar o acesso HTTP das fontes · rodada de legibilidade · revisão @cristiano.albino · 25/11
- [ ] **T79** Separar a escolha da IA e o que os provedores repetem · rodada de legibilidade · revisão @luiz.pagliari · 25/11
- [ ] **T80** Separar as travas por assunto · rodada de legibilidade · revisão @cristiano.albino · 25/11
- [ ] **T81** Separar regras, mecanismo e textos das checagens e do plano · rodada de legibilidade · revisão @geison.santos · 26/11
- [ ] **T82** Separar instalação, terminal e captura por papel · rodada de legibilidade · revisão @ali.santos · 26/11
- [ ] **T83** Trocar abreviações por nomes completos no Python · rodada de legibilidade · revisão @luiz.pagliari · 26/11
- [ ] **T84** Trocar código esperto por laço e função com nome · rodada de legibilidade · revisão @cristiano.albino · 26/11
- [ ] **T85** Organizar as pastas do frontend por responsabilidade · rodada de legibilidade · revisão @halan.bacca · 26/11
- [ ] **T86** Juntar o comportamento repetido e dividir o App · rodada de legibilidade · revisão @halan.bacca · 26/11
- [ ] **T87** Dividir os componentes grandes da tela · rodada de legibilidade · revisão @halan.bacca · 26/11
- [ ] **T88** Padronizar os nomes do frontend · rodada de legibilidade · revisão @halan.bacca · 26/11
- [ ] **T90** Achatar ifs encadeados e laços no Python · rodada de legibilidade · revisão @ali.santos · 26/11
- [ ] **T91** Achatar ifs encadeados e laços no frontend · rodada de legibilidade · revisão @halan.bacca · 26/11
- [ ] **T92** Separar o histórico e versionar a decisão 11 · rodada de legibilidade · revisão @cristiano.albino · 26/11
- [ ] **T93** Numerar as travas como a decisão 06 · rodada de legibilidade · revisão @cristiano.albino · 26/11
- [ ] **T94** Reescrever o README no ritmo do Como usar · rodada de legibilidade · revisão @halan.bacca · 26/11
- [ ] **T95** Deixar o README técnico só para desenvolvimento · rodada de legibilidade · revisão @luiz.pagliari · 26/11
- [ ] **T96** Enxugar a spec viva, as decisões e o steering · rodada de legibilidade · revisão @geison.santos · 26/11
- [ ] **T89** Atualizar diagrama, steering e documentação para a estrutura nova · rodada de legibilidade · revisão @geison.santos · 26/11
- [ ] **T97** Deixar o replay da visita mais discreto · ajustes do relatório · sem revisor · commit 6800929 · ajuste 32f0ac8 · 27/11
- [ ] **T98** Baixar as falhas em CSV e o relatório completo · ajustes do relatório · sem revisor · commit ea7a594 · 27/11
- [ ] **T99** Mostrar os créditos do Kiro ou os tokens do Claude e do Codex · ajustes do relatório · sem revisor · 27/11

## A fazer

### Fase 0. Preparar

_(vazio)_

### Fase 1. Núcleo determinístico

_(vazio)_

### Fase 2. Relatório HTML

_(vazio)_

### Fase 3. IA

_(vazio)_

### Fase 4. Entregar

- [ ] **T42** Instalar do zero no Windows e no Linux · fase 4 · 04–08/12 · revisão @ali.santos
- [ ] **T47** Gravar a apresentação e o demo · fase 4 · 04–08/12 · revisão @halan.bacca
- [ ] **T48** Preparar a versão final · fase 4 · 04–08/12 · revisão @luiz.pagliari

### Extensão: OSV e NVD (só se houver tempo, até 02/12)

_(vazio)_

### Extensão: gravar a visita (branch `feat/gravar`, só se houver tempo, até 08/12)

_(vazio)_

### Extensão: validações de segurança ativas (até 30/11)

_(vazio)_

### Rodada de legibilidade (até 08/12)


## Feito

- [x] **S02** Commitar a spec no `main` (ponto de partida f36fe80) · 06/11
- [x] **S03** Coletar os e-mails do Git dos revisores para a linha `Co-authored-by` · antes da fase 1 · feito 06/11
