# Verificação no Linux

Resultado dos comandos da seção "Verificação" do README, rodados na máquina local.

| | |
|---|---|
| Data | 09/11/2026 |
| Código | commit a61e8f8 (código da T51; a T44 não muda código) |
| Sistema | Linux Mint 21.3 (kernel 5.15) |
| Python | 3.10.12, no `.venv` do projeto |
| Ferramentas | `requirements-dev.txt`: pytest 9.2.0, pytest-cov 7.1.0, ruff 0.17.4, mypy 2.4.1 |
| Resultado | os três comandos passam; 695 testes; cobertura total de 99% e de 99% nas regras de negócio |

O relatório HTML, arquivo por arquivo e linha por linha, está em [`html/index.html`](html/index.html).

## `ruff check`

```
All checks passed!
```

## `mypy rastro`

```
Success: no issues found in 53 source files
```

## `pytest --cov=rastro --cov-report=term`

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.2.0, pluggy-1.7.0
rootdir: <raiz do projeto>
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collected 695 items

tests/acao/test_plano.py .......................                         [  3%]
tests/acao/test_task.py .....                                            [  4%]
tests/configuracao/test_checagens.py ................................... [  9%]
.....................................                                    [ 14%]
tests/explicacao/test_ia.py ......................                       [ 17%]
tests/fontes/test_github_advisory.py ....................                [ 20%]
tests/fontes/test_juncao.py ............                                 [ 22%]
tests/fontes/test_nvd.py .....................                           [ 25%]
tests/fontes/test_osv.py ...........................                     [ 29%]
tests/fontes/test_registro_npm.py ...............................        [ 33%]
tests/har/test_leitor.py ......................                          [ 36%]
tests/har/test_site.py .......                                           [ 37%]
tests/ia/provedores/test_claude.py ...............                       [ 39%]
tests/ia/provedores/test_codex.py .......................                [ 43%]
tests/ia/provedores/test_kiro.py ...........                             [ 44%]
tests/ia/test_cliente.py .................                               [ 47%]
tests/ia/test_sanitizacao.py ..................                          [ 49%]
tests/identificacao/test_assinaturas.py ................................ [ 54%]
.....................                                                    [ 57%]
tests/identificacao/test_bundles.py ............                         [ 59%]
tests/identificacao/test_ia.py ..................                        [ 61%]
tests/relatorio/test_gravacao.py ............................            [ 65%]
tests/relatorio/test_html.py ........                                    [ 66%]
tests/relatorio/test_json.py ............................                [ 70%]
tests/risco/test_nota.py ..........                                      [ 72%]
tests/risco/test_prioridade.py ............                              [ 74%]
tests/test_cli.py .........................                              [ 77%]
tests/test_fluxo.py ..................                                   [ 80%]
tests/test_rede_bloqueada.py ...                                         [ 80%]
tests/travas/test_ancoragem.py .......................                   [ 84%]
tests/travas/test_codigo_publicado.py .............................      [ 88%]
tests/travas/test_conferencia.py .......                                 [ 89%]
tests/travas/test_explicacao.py ....................                     [ 92%]
tests/travas/test_faixa_de_versao.py ................................    [ 96%]
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
rastro/cli.py                           105      0   100%
rastro/configuracao/__init__.py           0      0   100%
rastro/configuracao/checagens.py        140      0   100%
rastro/configuracao/modelos.py           20      0   100%
rastro/explicacao/__init__.py             0      0   100%
rastro/explicacao/ia.py                  80      0   100%
rastro/explicacao/modelos.py              8      0   100%
rastro/fluxo.py                         123      0   100%
rastro/fontes/__init__.py                 0      0   100%
rastro/fontes/conector.py                29      0   100%
rastro/fontes/github_advisory.py         89      0   100%
rastro/fontes/juncao.py                  59      0   100%
rastro/fontes/nvd.py                     86      0   100%
rastro/fontes/osv.py                     79      0   100%
rastro/fontes/registro_npm.py           112      1    99%
rastro/har/__init__.py                    0      0   100%
rastro/har/leitor.py                    122      2    98%
rastro/har/modelos.py                    17      0   100%
rastro/har/site.py                       15      0   100%
rastro/ia/__init__.py                     0      0   100%
rastro/ia/cliente.py                     73      0   100%
rastro/ia/provedores/__init__.py          0      0   100%
rastro/ia/provedores/claude.py           52      0   100%
rastro/ia/provedores/codex.py            69      0   100%
rastro/ia/provedores/kiro.py             26      0   100%
rastro/ia/sanitizacao.py                 20      0   100%
rastro/identificacao/__init__.py          0      0   100%
rastro/identificacao/assinaturas.py      85      0   100%
rastro/identificacao/bundles.py          61      0   100%
rastro/identificacao/ia.py               59      0   100%
rastro/identificacao/modelos.py          18      0   100%
rastro/relatorio/__init__.py              0      0   100%
rastro/relatorio/gravacao.py             52      0   100%
rastro/relatorio/html.py                 17      0   100%
rastro/relatorio/json.py                 89      0   100%
rastro/risco/__init__.py                  0      0   100%
rastro/risco/modelos.py                  16      0   100%
rastro/risco/nota.py                     26      0   100%
rastro/risco/prioridade.py               26      0   100%
rastro/travas/__init__.py                 0      0   100%
rastro/travas/ancoragem.py               46      0   100%
rastro/travas/codigo_publicado.py        57      0   100%
rastro/travas/conferencia.py             51      0   100%
rastro/travas/explicacao.py              34      0   100%
rastro/travas/faixa_de_versao.py        103      0   100%
rastro/travas/formato.py                 86      0   100%
rastro/travas/modelos.py                  6      0   100%
---------------------------------------------------------
TOTAL                                  2279      6    99%
============================= 695 passed in 12.15s =============================
```

O `__main__.py` aparece com 0% porque o teste `test_python_m_rastro_help_retorna_0` o executa em outro processo, que o `pytest-cov` não mede.
