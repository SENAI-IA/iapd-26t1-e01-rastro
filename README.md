# Rastro

Rastro lê um arquivo HAR, identifica as bibliotecas front-end do site, cruza com o GitHub Advisory (CVE, CVSS, EPSS) e gera um relatório de risco explicado por IA. Só análise passiva.

Projeto final do curso de IA aplicada (tema Produtividade do SENAI) · grupo E01 IA SEC.

> **Status:** fase 0. Já existem o esqueleto Python (`python -m rastro --help`) e a verificação local; a análise do HAR começa na fase 1. Andamento no [kanban](.kiro/specs/rastro-mvp/kanban.md).

## Onde está cada coisa

| Pasta | Conteúdo |
|---|---|
| `.kiro/steering/` | Padrões de construção que o agente de IA segue: produto, tecnologia, estrutura, processo, Python e React. |
| `.kiro/specs/rastro-mvp/` | Spec do MVP: requisitos em EARS, design, tasks (com revisor) e kanban. |
| `.kiro/skills/rastro-nova-regra/` | Skill do projeto: passo a passo para acrescentar checagem, assinatura, fonte de dados, provedor de IA ou trava, com teste, cobertura e verificação. |
| `docs/` | Entregáveis: `pitch-inicial.pdf`, `spike/` (validações da fase 0) e `cobertura/` (resultado da verificação em cada sistema). Depois: decisões. |

## Verificação

Não há CI: a verificação roda na máquina local, no Linux e no Windows, antes de cada entrega. Precisa só do Python 3.10 ou mais novo. As ferramentas, com versão fixa no `requirements-dev.txt`, ficam no `.venv` do projeto; nada é instalado globalmente.

Na raiz do projeto:

| Passo | Linux | Windows (PowerShell) |
|---|---|---|
| 1. Criar o `.venv` (uma vez) | `python3 -m venv .venv` | `py -m venv .venv` |
| 2. Ativar o `.venv` | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| 3. Instalar as ferramentas (uma vez) | `pip install -r requirements-dev.txt` | `pip install -r requirements-dev.txt` |
| 4. Estilo e erros comuns | `ruff check` | `ruff check` |
| 5. Tipos | `mypy rastro` | `mypy rastro` |
| 6. Testes e cobertura | `pytest --cov=rastro --cov-report=term` | `pytest --cov=rastro --cov-report=term` |

- Se o PowerShell recusar a ativação, libere só para a janela aberta: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
- Passou quando o `ruff` mostra `All checks passed!`, o `mypy` mostra `Success` e o `pytest` termina sem falhas. Os testes não acessam a rede.
- O resultado de cada sistema fica em `docs/cobertura/linux.md` e `docs/cobertura/windows.md`: data, commit, versões e a saída dos três comandos.

## Como trabalhamos

- A spec vem antes do código. Cada task do `tasks.md` é pequena e tem entrega, critério de aceite, arquivos, teste e requisito.
- Um commit por task, direto no `main`, semântico e em pt-BR: `feat(risco): calcular nota de risco pela fórmula fixa (T17)`, com o revisor como coautor. A revisão vem depois do commit; ajuste vira um commit `fix` novo.
- Regras completas em `.kiro/steering/processo.md`.

## Links

- Pitch: [`docs/pitch-inicial.pdf`](docs/pitch-inicial.pdf)
