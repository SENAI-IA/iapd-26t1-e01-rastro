# Rastro

Rastro lê um arquivo HAR, identifica as bibliotecas front-end do site, cruza com o GitHub Advisory (CVE, CVSS, EPSS) e gera um relatório de risco explicado por IA. Só análise passiva.

Projeto final do curso de IA aplicada (tema Produtividade do SENAI) · grupo E01 IA SEC.

> **Status:** spec escrita e em revisão; a construção começa pela fase 0. Ainda não há código para rodar. Andamento no [kanban](.kiro/specs/rastro-mvp/kanban.md).

## Onde está cada coisa

| Pasta | Conteúdo |
|---|---|
| `.kiro/steering/` | Padrões de construção que o agente de IA segue: produto, tecnologia, estrutura, processo, Python e React. |
| `.kiro/specs/rastro-mvp/` | Spec do MVP: requisitos em EARS, design, tasks (com revisor) e kanban. |
| `.kiro/skills/rastro-nova-regra/` | Skill do projeto. A criar. |
| `docs/` | Entregáveis: `pitch-inicial.pdf`. Depois: decisões, cobertura. |

## Como trabalhamos

- A spec vem antes do código. Cada task do `tasks.md` é pequena e tem entrega, critério de aceite, arquivos, teste e requisito.
- Um commit por task, direto no `main`, semântico e em pt-BR: `feat(risco): calcular nota de risco pela fórmula fixa (T17)`, com o revisor como coautor. A revisão vem depois do commit; ajuste vira um commit `fix` novo.
- Regras completas em `.kiro/steering/processo.md`.

## Links

- Pitch: [`docs/pitch-inicial.pdf`](docs/pitch-inicial.pdf)
