# Verificação no Linux

Resultado dos comandos da seção "Verificação" do README, rodados na máquina local.

| | |
|---|---|
| Data | 10/11/2026 |
| Código | commit b73056d (código da T54 e dos ajustes do code review) |
| Sistema | Linux Mint 21.3 (kernel 5.15) |
| Python | 3.10.12, no `.venv` do projeto |
| Ferramentas | `requirements-dev.txt`: pytest 9.2.0, pytest-cov 7.1.0, ruff 0.17.4, mypy 2.4.1 |
| Resultado | os três comandos passam; 737 testes; cobertura total de 99% e de 99% nas regras de negócio |

O relatório HTML, arquivo por arquivo e linha por linha, está em [`html/index.html`](html/index.html).

## `ruff check`

```
All checks passed!
```

## `mypy rastro`

```
Success: no issues found in 56 source files
```

## `pytest --cov=rastro --cov-report=term`

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.2.0, pluggy-1.7.0
rootdir: <raiz do projeto>
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 737 items

tests/acao/test_plano.py .......................                         [  3%]
tests/acao/test_task.py .....                                            [  3%]
tests/configuracao/test_checagens.py ................................... [  8%]
......................................                                   [ 13%]
tests/explicacao/test_ia.py ......................                       [ 16%]
tests/fontes/test_consulta.py ..                                         [ 16%]
tests/fontes/test_github_advisory.py ......................              [ 19%]
tests/fontes/test_juncao.py ............                                 [ 21%]
tests/fontes/test_nvd.py .......................                         [ 24%]
tests/fontes/test_osv.py .............................                   [ 28%]
tests/fontes/test_registro_npm.py ....................................   [ 33%]
tests/har/test_leitor.py ................................                [ 37%]
tests/har/test_site.py .......                                           [ 38%]
tests/har/test_visita.py .....                                           [ 39%]
tests/ia/provedores/test_claude.py ...............                       [ 41%]
tests/ia/provedores/test_codex.py .......................                [ 44%]
tests/ia/provedores/test_kiro.py ...........                             [ 46%]
tests/ia/test_cliente.py ..................                              [ 48%]
tests/ia/test_sanitizacao.py .....................                       [ 51%]
tests/identificacao/test_assinaturas.py ................................ [ 55%]
.....................                                                    [ 58%]
tests/identificacao/test_bundles.py ............                         [ 60%]
tests/identificacao/test_ia.py ...................                       [ 62%]
tests/relatorio/test_gravacao.py ............................            [ 66%]
tests/relatorio/test_html.py ........                                    [ 67%]
tests/relatorio/test_json.py ...............................             [ 71%]
tests/risco/test_achados.py ..                                           [ 72%]
tests/risco/test_nota.py ..........                                      [ 73%]
tests/risco/test_prioridade.py ............                              [ 75%]
tests/test_cli.py ..........................                             [ 78%]
tests/test_fluxo.py ...................                                  [ 81%]
tests/test_rede_bloqueada.py ...                                         [ 81%]
tests/travas/test_ancoragem.py .......................                   [ 84%]
tests/travas/test_codigo_publicado.py .............................      [ 88%]
tests/travas/test_conferencia.py .......                                 [ 89%]
tests/travas/test_explicacao.py ....................                     [ 92%]
tests/travas/test_faixa_de_versao.py .................................   [ 96%]
tests/travas/test_formato.py .......................                     [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.10.12-final-0 _______________

Name                                  Stmts   Miss  Cover
---------------------------------------------------------
rastro/__init__.py                        0      0   100%
rastro/__main__.py                        3      3     0%
rastro/acao/__init__.py                   0      0   100%
rastro/acao/modelos.py                   18      0   100%
rastro/acao/plano.py                     90      0   100%
rastro/acao/task.py                      12      0   100%
rastro/cli.py                           110      0   100%
rastro/configuracao/__init__.py           0      0   100%
rastro/configuracao/checagens.py        141      0   100%
rastro/configuracao/modelos.py           20      0   100%
rastro/explicacao/__init__.py             0      0   100%
rastro/explicacao/ia.py                  77      0   100%
rastro/explicacao/modelos.py              8      0   100%
rastro/fluxo.py                          76      0   100%
rastro/fontes/__init__.py                 0      0   100%
rastro/fontes/conector.py                29      0   100%
rastro/fontes/consulta.py                47      0   100%
rastro/fontes/github_advisory.py         94      0   100%
rastro/fontes/juncao.py                  59      0   100%
rastro/fontes/nvd.py                     91      0   100%
rastro/fontes/osv.py                     84      0   100%
rastro/fontes/registro_npm.py           128      1    99%
rastro/har/__init__.py                    0      0   100%
rastro/har/leitor.py                    143      2    99%
rastro/har/modelos.py                    20      0   100%
rastro/har/site.py                       23      0   100%
rastro/har/visita.py                     33      0   100%
rastro/ia/__init__.py                     0      0   100%
rastro/ia/cliente.py                     74      0   100%
rastro/ia/provedores/__init__.py          0      0   100%
rastro/ia/provedores/claude.py           52      0   100%
rastro/ia/provedores/codex.py            69      0   100%
rastro/ia/provedores/kiro.py             26      0   100%
rastro/ia/sanitizacao.py                 31      0   100%
rastro/identificacao/__init__.py          0      0   100%
rastro/identificacao/assinaturas.py      85      0   100%
rastro/identificacao/bundles.py          61      0   100%
rastro/identificacao/ia.py               63      0   100%
rastro/identificacao/modelos.py          18      0   100%
rastro/relatorio/__init__.py              0      0   100%
rastro/relatorio/gravacao.py             52      0   100%
rastro/relatorio/html.py                 17      0   100%
rastro/relatorio/json.py                133      0   100%
rastro/risco/__init__.py                  0      0   100%
rastro/risco/achados.py                  11      0   100%
rastro/risco/modelos.py                  16      0   100%
rastro/risco/nota.py                     26      0   100%
rastro/risco/prioridade.py               26      0   100%
rastro/travas/__init__.py                 0      0   100%
rastro/travas/ancoragem.py               46      0   100%
rastro/travas/codigo_publicado.py        57      0   100%
rastro/travas/conferencia.py             51      0   100%
rastro/travas/explicacao.py              34      0   100%
rastro/travas/faixa_de_versao.py        104      0   100%
rastro/travas/formato.py                 86      0   100%
rastro/travas/modelos.py                  6      0   100%
---------------------------------------------------------
TOTAL                                  2450      6    99%
Coverage HTML written to dir docs/cobertura/html
============================= 737 passed in 7.39s ==============================
```

O `__main__.py` aparece com 0% porque o teste `test_r14_7_python_m_rastro_help_retorna_0` o executa em outro processo, que o `pytest-cov` não mede.
