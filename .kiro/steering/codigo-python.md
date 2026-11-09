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
- **Tipos em tudo:** type hints em funções; `dataclass` para modelos (`Biblioteca`, `Achado`, `Requisicao`, `Checagem`).
- `ruff` e `mypy` sem erros.

## Regras

- Regras de negócio são funções puras: sem arquivo, rede, IA ou relógio dentro delas.
- Entrada e saída só nas bordas (`cli.py`, `har/leitor.py`, `fontes/`, `ia/`, `relatorio/`).
- A IA é chamada só por `ia/cliente.py`, e o que ela devolve passa por `travas/` antes de virar dado. A IA nunca preenche CVE, versão, CVSS, EPSS, nota ou versão-alvo.
- Prompts ficam em `ia/prompts/`, nunca como texto solto no meio do código.
- Erro que encerra a análise é uma exceção da borda com a mensagem pronta (ex.: `HarInvalido`). Só o `cli.py` a transforma em mensagem na saída de erro e código 1.

## Portabilidade e segurança

- `pathlib` para caminhos; `encoding="utf-8"` em toda leitura e escrita.
- CLI de IA: executável via `shutil.which`, prompt pela entrada padrão, saída lida como UTF-8, tempo limite definido.
- Relatório gravado com `open(caminho, "x", encoding="utf-8")` numa pasta nova por análise: nunca sobrescreve.
- Pacote do npm lido só em memória (`tarfile` + `extractfile`); nunca `extract`/`extractall`, nunca executar.
- Nunca enviar à IA cookies, cabeçalhos de autenticação ou tokens do HAR; só os trechos necessários.

## Testes

- Um arquivo de teste por módulo, espelhando `rastro/` em `tests/`.
- Fonte de dados e IA trocadas por dublês; nenhum teste acessa rede.
- Dublês usados por mais de um arquivo de teste (`ConectorFalso`, `RegistroFalso`) ficam em `tests/dubles.py`; o resto fica no próprio teste.
- Nome do teste leva o critério da spec e descreve o comportamento: `test_r05_2_prioridade_alta_a_partir_de_7_5`.
- Arquivos de entrada dos testes ficam em `tests/dados/`, feitos à mão, pequenos e sem dado real (cookie e token só com valor fictício).
- Um `conftest.py` bloqueia acesso à rede em todos os testes.
