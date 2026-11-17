# Verificação no Linux

Resultado dos comandos da seção "Verificação" do README, rodados na máquina local.

| | |
|---|---|
| Data | 17/11/2026 |
| Código de partida | `46959c7` |
| Sistema | Linux |
| Python | 3.10.12, no `.venv` do projeto |
| Ferramentas | pytest 9.2.0, pytest-cov 7.1.0, ruff 0.17.4, mypy 2.4.1 |
| Resultado | os três comandos passam; 788 testes; cobertura total de 96% e 97% nas regras de negócio |

A cobertura das regras de negócio inclui `rastro/pentest/`. O HTML detalhado pode ser atualizado com:

```bash
pytest --cov=rastro --cov-report=term --cov-report=html:docs/cobertura/html
```

## `ruff check`

```
All checks passed!
```

## `mypy rastro`

```
Success: no issues found in 67 source files
```

## `pytest --cov=rastro --cov-report=term`

```
============================= test session starts ==============================
collected 788 items
...
============================= 788 passed in 3.5s ===============================
```

Resumo da cobertura:

```text
Regras de negócio (inclui pentest): 2362 linhas, 77 sem teste, 97%
Total do pacote rastro: 3370 linhas, 141 sem teste, 96%
```

Não há CI. A verificação deve ser repetida localmente no Linux e no Windows antes da entrega. Os testes não acessam a rede nem executam uma CLI de IA real.
