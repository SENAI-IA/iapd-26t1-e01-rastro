# Processo

## Desenvolvido com IA, guiado pela spec

- A spec (`.kiro/specs/rastro-mvp/`: requirements, design, tasks) vem antes do código.
- Cada tarefa do `tasks.md` é marcada como concluída **no mesmo commit** que a implementa.
- Steering e skill são atualizados no mesmo commit da mudança de padrão.
- O README tem a seção "Desenvolvido com IA", apontando spec, steering e skill e como foram usados.

## Tasks bem definidas

Toda tarefa do `tasks.md` é pequena e fechada antes de começar. Cada uma tem:

- **Número e título com verbo:** `T07 Calcular a nota de risco`.
- **Entrega:** o que passa a existir ao final, em uma frase.
- **Critério de aceite:** como saber que terminou (comando que roda, teste que passa, tela que aparece).
- **Arquivos:** onde a mudança acontece.
- **Teste:** qual teste prova a regra, quando houver regra de negócio.
- **Requisito:** os critérios `Rxx.y` da spec que ela atende.
- **Revisão:** quem revisa (por área, dividido entre os membros).

Tamanho: até meio dia de trabalho. Se a descrição precisa de "e", são duas tasks. Task que não cabe nisso é quebrada antes de começar, não no meio.

## Commits semânticos, um por task

- **Uma task, um commit**, direto no `main`. O commit traz o código, os testes, a marcação `[x]` no `tasks.md`, o cartão do kanban e o `Co-authored-by` do revisor. Nada de misturar duas tasks no mesmo commit.
- **Formato** (Conventional Commits, descrição em pt-BR, no imperativo):

  ```
  <tipo>(<escopo>): <o que muda> (T07)

  <por que, quando não for óbvio>
  ```

- **Tipos:** `feat` (funcionalidade), `fix` (correção), `test` (só testes), `refactor` (sem mudar comportamento), `docs` (documentação, spec, steering, decisões), `build` (dependências, Vite), `chore` (manutenção que não cabe nos outros).
- **Escopo:** a pasta do núcleo ou a área (`har`, `identificacao`, `travas`, `fontes`, `risco`, `configuracao`, `explicacao`, `acao`, `ia`, `relatorio`, `cli`, `frontend`, `spec`, `steering`).
- **Exemplos:**
  - `feat(risco): calcular nota de risco pela fórmula fixa (T07)`
  - `test(har): cobrir HAR sem conteúdo de resposta (T03)`
  - `docs(spec): detalhar critérios de aceite do RF04`
- Mudança fora de task (ajuste de doc, correção pequena) também segue o formato, só sem o número.
- O histórico precisa contar o desenvolvimento guiado pela spec: lendo o `git log`, a banca vê task por task.

## Autoria, revisão e kanban

- **Tudo direto no `main`, sem branch e sem MR**, uma task por vez, um commit por task. Push logo depois.
- Antes do commit, `ruff`, `mypy` e `pytest` passam na máquina local.
- **Revisor é coautor desde o commit:** a mensagem termina com `Co-authored-by: <Nome> <e-mail do Git>`. Tabela dos revisores no `tasks.md`.
- **Revisão depois do commit:** o revisor confere o commit (`git show`), o critério de aceite e a verificação. Ajuste vira commit novo `fix(...) (Tnn)`. Commit enviado nunca é reescrito.
- **Estado no `kanban.md`:** o cartão anda (a fazer → em andamento → em revisão → feito) junto com os commits. Uma task em andamento por vez e no máximo 3 em revisão.

## Documentos que andam juntos

Mudou o escopo? Atualize, no mesmo commit:

- o PRD,
- o pitch,
- a spec.

E gere de novo os PDFs do PRD e do pitch.

## Decisões

- Cada decisão importante vira um arquivo em `docs/decisoes/`: contexto, decisão, alternativas consideradas.
- Exemplos: fórmula da nota, uma só fonte de dados, papel da IA, IA por CLI, React no relatório.
- São as respostas prontas para a banca. O porquê fica aqui, não em comentário no código.

## Idioma

Português do Brasil em tudo: código, nomes, testes, commits, documentação, prompts e interface. Inglês só no que vem de bibliotecas e da linguagem.

## Entregas (10/12/2026, 23h59; meta interna 08/12)

- MVP 100% funcional em Windows e Linux.
- PRD final em `docs/prd.pdf` (T48).
- README que outra pessoa consegue seguir para instalar na própria máquina (Windows e Linux). Sem Docker: o demo gravado cumpre o requisito "Docker ou vídeo".
- Relatório de cobertura no repo (≥ 60% nas regras de negócio).
- Spec, steering e skill versionados.
- Gravação da apresentação de slides, narrada.
- Gravação do demo: do HAR exportado ao relatório e à task aberta.
