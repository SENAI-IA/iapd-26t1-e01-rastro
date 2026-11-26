# Verificação no Linux

Resultado dos comandos da seção [Verificação](../../README-TECNICO.md#verificação) do README técnico, rodados na máquina local.

| | |
|---|---|
| Data | 26/11/2026 |
| Código de partida | `7b9a6da` (depois da rodada de legibilidade, T72 a T96) |
| Sistema | Linux |
| Python | 3.10.12, no `.venv` do projeto |
| Ferramentas | pytest 9.2.0, pytest-cov 7.1.0, ruff 0.17.4, mypy 2.4.1 |
| Resultado | os três comandos passam; 1056 testes; cobertura total de 96% e 97% nas regras de negócio |

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
Success: no issues found in 133 source files
```

## `pytest --cov=rastro --cov-report=term`

```
============================= test session starts ==============================
collected 1056 items
...
============================= 1056 passed in 10.3s ==============================
```

Resumo da cobertura:

```text
Regras de negócio (inclui pentest): 2734 linhas, 85 sem teste, 97%
Total do pacote rastro: 4847 linhas, 208 sem teste, 96%
```

Não há CI. A verificação deve ser repetida localmente no Linux e no Windows antes da entrega. Os testes não acessam a rede nem executam uma CLI de IA real.
