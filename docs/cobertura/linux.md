# Verificação no Linux

Resultado dos comandos da seção "Verificação" do README, rodados na máquina local.

| | |
|---|---|
| Data | 06/11/2026 |
| Código | commit 6a52bb3 (esqueleto da T05) |
| Sistema | Linux Mint 21.3 (kernel 5.15) |
| Python | 3.10.12, no `.venv` do projeto |
| Ferramentas | `requirements-dev.txt`: pytest 9.2.0, pytest-cov 7.1.0, ruff 0.17.4, mypy 2.4.1 |
| Resultado | os três comandos passam; cobertura total de 75% |

## `ruff check`

```
All checks passed!
```

## `mypy rastro`

```
Success: no issues found in 3 source files
```

## `pytest --cov=rastro --cov-report=term`

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.2.0, pluggy-1.7.0
rootdir: <raiz do projeto>
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 6 items

tests/test_cli.py ...                                                    [ 50%]
tests/test_rede_bloqueada.py ...                                         [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.10.12-final-0 _______________

Name                 Stmts   Miss  Cover
----------------------------------------
rastro/__init__.py       0      0   100%
rastro/__main__.py       3      3     0%
rastro/cli.py            9      0   100%
----------------------------------------
TOTAL                   12      3    75%
============================== 6 passed in 0.12s ===============================
```

O `__main__.py` aparece com 0% porque o teste `test_python_m_rastro_help_retorna_0` o executa em outro processo, que o `pytest-cov` não mede. Ainda não há regra de negócio: a meta de 60% (R19.1) passa a valer a partir da fase 1.
