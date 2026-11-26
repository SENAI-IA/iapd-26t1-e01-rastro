---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# Código Python

O código será defendido na banca. Qualquer pessoa deve entender um arquivo sem ajuda.

## Legibilidade

- **Nomes que dizem o que é, em português, sem abreviação:** `calcular_nota_de_risco(cvss, percentil_epss)`, não `calc(a, b)`.
- **Funções curtas, um nível de abstração cada.**
- **Evitar comentários.** Lógica complexa vira função com nome que se explica. Condição composta vira função: `biblioteca_esta_vulneravel(...)` em vez de um `if` com três condições.
- **Sem código esperto:** `if` claro em vez de expressão encadeada; laço legível em vez de compreensão aninhada.
  - Compreensão só com um `for` e, se tiver filtro, filtro curto; dois `for` ou filtro longo viram laço ou função com nome.
  - Sem `lambda`: o que vai para `sorted(key=...)`, `re.sub`, `signal.signal` ou callback é uma função com nome (função interna quando precisa de uma variável local, como `pedir_parada_pelo_ctrl_c`).
  - `any`/`all` com um `for` e uma condição com nome (`any(tem_identificador_em_comum(aviso, outro) for outro in grupo)`); contagem é um laço que soma, não `sum(1 for ...)`.
  - Ternário só em uma linha e sem encadear; `x or []`, `x or {}` e `a or b or ""` no meio de expressões longas viram função com `if`.
  - Sem desempacotar com estrela (`[*lista, x]`, `a, *resto = ...`, `**asdict(...)`): passos com nome (`lista + [x]`, `partes[0]` e `partes[1:]`, `dicionario.update(...)`).
  - Números com significado viram constante com nome (`SEGUNDOS_POR_MINUTO`, `ORDEM_DA_PARTE_NUMERICA`, `ESPACOS_DE_RECUO_DO_JSON`).
  - Truque de baixo nível necessário (`os.dup2`, `ExitStack.callback`, `object_pairs_hook`, OU de bits) fica dentro de função cujo nome diz o que ele faz.
- **Caminho plano, sem escada de blocos** (`ruff` com `C901`, `max-complexity = 5` no `pyproject.toml`; `tests/test_legibilidade_do_codigo.py` barra função com mais de dois níveis de bloco aninhado: `if`, `for`, `while`, `with`, `try` e `match` contam, `elif` não soma, função interna recomeça). Sem `noqa` nem exceção por arquivo.
  - Guarda: o caso especial sai logo no começo e o caminho normal segue sem recuo (`if not medicoes: return None`).
  - Tabela: cadeia que só escolhe um valor vira dicionário constante com nome (`COMPARACAO_PELO_OPERADOR[condicao.operador]`, `ARQUIVO_PELO_NOME_DO_SHELL.get(nome, ARQUIVO_DE_QUALQUER_SHELL)`).
  - Função por volta: laço com mais de uma decisão chama uma função que diz o que cada volta faz (`for requisicao in requisicoes: alvo = alvo_ainda_nao_visto(requisicao, site, alvos_ja_vistos)`); flag que só serve para sair do laço vira `return` ou `any(...)` com condição nomeada.
- **Regex:** toda regex é uma constante com nome que diz o que ela encontra. A longa usa `re.VERBOSE`, com uma parte por linha; a que junta pedaços é montada de constantes com nome e sem f-string. Grupo usado no código é nomeado (`(?P<versao>...)` e `group("versao")`), nunca por índice.
- **Funções comuns sem camada:** `sem_repeticao(itens)` (`rastro/listas.py`) tira repetidos mantendo a ordem (no lugar de `dict.fromkeys`); `ler_data_iso(texto)` (`rastro/data_e_hora.py`) lê data ISO 8601 aceitando o `Z` do UTC.
- **Tipos em tudo:** type hints em funções; `dataclass` para modelos (`Biblioteca`, `Achado`, `Requisicao`, `Checagem`).
- `ruff` e `mypy` sem erros.

## Regras

- Regras de negócio são funções puras: sem arquivo, rede, IA ou relógio dentro delas.
- Entrada e saída só nas bordas (`cli.py`, `comandos/`, `har/leitor_do_har.py`, `fontes/`, `ia/`, `relatorio/`, `pentest/leitura_do_resultado.py`, `pentest/gravacao_do_resultado.py`).
- A IA é chamada só por `ia/cliente.py`, e o que ela devolve passa por `travas/` antes de virar dado. A IA nunca preenche CVE, versão, CVSS, EPSS, nota ou versão-alvo.
- Prompts ficam em `ia/prompts/`, nunca como texto solto no meio do código.
- O prompt é lido por `ia/montagem_do_prompt.py` com `importlib.resources` e os dados entram no marcador `{{entrada}}` (`str.replace`, não `format`, porque o exemplo do prompt tem chaves de JSON).
- Erro que encerra a análise é uma exceção da borda com a mensagem pronta (ex.: `HarInvalido`). Só os arquivos de `comandos/` a transformam em mensagem na saída de erro e código 1 (com `encerrar_com_erro`, de `comandos/saida_de_erro.py`).

## Portabilidade e segurança

- `pathlib` para caminhos; `encoding="utf-8"` em toda leitura e escrita.
- CLI de IA: executável via `shutil.which` (`ia/escolha_da_ia.py`); rodada só por `ia/provedores/execucao_da_cli.py`, com prompt pela entrada padrão, saída lida como UTF-8 e tempo limite definido.
- Relatório gravado com `open(caminho, "x", encoding="utf-8")` numa pasta nova por análise: nunca sobrescreve.
- Pacote do npm lido só em memória (`tarfile` + `extractfile`); nunca `extract`/`extractall`, nunca executar.
- Nunca enviar à IA cookies, cabeçalhos de autenticação ou tokens do HAR; só os trechos necessários.

## Testes

- Um arquivo de teste por módulo, espelhando `rastro/` em `tests/`.
- Fonte de dados e IA trocadas por dublês; nenhum teste acessa rede.
- Dublês usados por mais de um arquivo de teste (`ConectorFalso`, `RegistroFalso`, `ProvedorFalso`) ficam em `tests/dubles.py`; o resto fica no próprio teste.
- Ajudantes de teste usados por mais de um arquivo ficam num `apoio.py` da pasta do módulo (ex.: `tests/instalacao/apoio.py`, `tests/terminal/apoio.py`).
- Nome do teste leva o critério da spec e descreve o comportamento: `test_r05_2_prioridade_alta_a_partir_de_7_5`.
- Arquivos de entrada dos testes ficam em `tests/dados/`, feitos à mão, pequenos e sem dado real (cookie e token só com valor fictício).
- Um `conftest.py` bloqueia acesso à rede em todos os testes.
