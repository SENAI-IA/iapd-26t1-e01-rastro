# Spike: CLIs de IA sem interação (T02)

Exploração de 06/11/2026 para preencher a tabela de provedores da seção 11 do design. Afeta R14.4 e R18.1.

**Só o Linux foi conferido.** O Windows fica para a T42 (instalação do zero), com um colega que use Windows. A seção "A conferir no Windows" lista o que olhar.

## Como foi feito

Um script com a biblioteca padrão, fora do repositório, chamou cada CLI do jeito que o Rastro vai chamar:

```python
subprocess.run(comando, input=prompt, capture_output=True, encoding="utf-8", timeout=180)
```

- Executável achado por `shutil.which`, rodando numa pasta vazia.
- O prompt foi um `explicar_achado` reduzido: jquery 3.4.1, GHSA-gxr4-xjj5-5px2, pedindo só um objeto JSON com três campos, com acentos para conferir o UTF-8.

| CLI | Versão | Instalada em |
|---|---|---|
| Claude Code | 2.1.319 | `~/.local/bin/claude` |
| Codex | 0.166.0 | `~/.local/bin/codex` |
| Kiro | kiro-cli 2.31.1 | `~/.local/bin/kiro-cli` |

Atenção: `/usr/bin/kiro` é o editor Kiro (IDE), não a CLI. O Rastro procura `kiro-cli`.

## Resultado no Linux

| | Claude | Codex | Kiro |
|---|---|---|---|
| Comando | `claude -p --output-format json --tools ""` | `codex exec --skip-git-repo-check --sandbox read-only --disable shell_tool --disable unified_exec --ephemeral --json -` | `kiro-cli chat --no-interactive --trust-tools=` |
| Prompt pela entrada padrão | funciona | funciona (o `-` manda ler a entrada) | funciona (sem argumento, lê a entrada) |
| Código de saída | 0 | 0 | 0 |
| Tempo | 6 a 7 s | 4 a 6 s | 9 a 11 s |
| Onde está a resposta | campo `result` do JSON | `text` do evento `item.completed` com `item.type == "agent_message"` | a saída padrão inteira, em texto |
| Tokens | `usage`: entrada = `input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens`; saída = `output_tokens` | `usage` do evento `turn.completed`: `input_tokens` e `output_tokens` | **não informa** (só créditos, ver abaixo) |
| Indica erro | código de saída e `is_error: true` | código de saída e ausência do `agent_message` | código de saída |
| JSON pedido veio limpo | sim | sim | sim |
| UTF-8 (acentos) | sim | sim | sim |

### Por que cada opção

- **Claude, `--tools ""`:** desliga as ferramentas. A IA só responde, não lê nem roda nada na máquina.
- **Claude, `--bare`:** não usar. Ele exige `ANTHROPIC_API_KEY` e ignora o login da CLI, o que vai contra "sem chave no projeto".
- **Codex, `--skip-git-repo-check`:** sem ele, o Codex se recusa a rodar fora de um repositório Git.
- **Codex, `--sandbox read-only`:** a IA não grava nada.
- **Codex, `--disable shell_tool --disable unified_exec`:** tira da IA as ferramentas de comando, como `--tools ""` no Claude e `--trust-tools=` no Kiro. Sem elas, um texto injetado no trecho do bundle não faz a IA ler arquivos da máquina. Na 0.166.0, a CLI aceita as duas opções sem erro, mas o efeito (a IA sem shell) **não foi conferido**: a chave de API do Codex do grupo foi removida antes do teste. Até ser conferido, para HAR de terceiros prefira o Kiro ou o Claude.
- **Codex, `--ephemeral`:** não grava a sessão em disco.
- **Codex, `--json`:** sem ele, a resposta sai limpa na saída padrão, mas os tokens só aparecem na saída de erro, em texto e no formato da localidade (`tokens used` / `12.813`). Com `--json`, os tokens vêm num campo.
- **Kiro, `--trust-tools=`:** não confia em nenhuma ferramenta. Sem resposta interativa, nenhuma ferramenta roda.
- **Kiro, saída em texto:** `--output-format stream-json` traz a resposta em pedaços e o `finalText` no evento `runFinished`, mas também não traz tokens: só `meteringUsage` em créditos (0,26 crédito na chamada) e `contextUsagePercentage`. Texto puro é mais simples e basta.

### Exemplos de resposta (resumidos)

Claude (`--output-format json`):

```json
{"type": "result", "subtype": "success", "is_error": false, "duration_ms": 3026,
 "result": "{\"o_que_e\": \"O jQuery 3.4.1 tem uma falha de XSS ...\", ...}",
 "usage": {"input_tokens": 2, "cache_creation_input_tokens": 15903,
           "cache_read_input_tokens": 11873, "output_tokens": 204},
 "total_cost_usd": 0.1337}
```

Codex (`--json`, uma linha por evento):

```json
{"type":"thread.started","thread_id":"..."}
{"type":"turn.started"}
{"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"{\"o_que_e\":\"...\"}"}}
{"type":"turn.completed","usage":{"input_tokens":12692,"cached_input_tokens":0,"output_tokens":152,"reasoning_output_tokens":57}}
```

Kiro (texto):

```
{"o_que_e": "O jQuery 3.4.1 tem uma falha de XSS na função htmlPrefilter, ...", "impacto": "...", "como_corrigir": "..."}
```

## Custo e tamanho do contexto

Cada CLI manda o próprio prompt de sistema junto com o nosso. Por isso a entrada fica muito maior que o prompt do Rastro, que tem menos de 100 tokens:

| CLI | Entrada | Saída | Custo informado |
|---|---|---|---|
| Claude (modelo padrão, Opus) | cerca de 24 a 27 mil | cerca de 200 | US$ 0,13 a 0,22 por chamada |
| Claude com `--model sonnet` | cerca de 24 mil | cerca de 220 | US$ 0,10 por chamada |
| Codex | cerca de 12,7 mil | cerca de 150 | não informa |
| Kiro | não informa | não informa | 0,26 crédito |

- Trocar o prompt de sistema do Claude (`--system-prompt`) não reduziu a entrada.
- O Rastro **não escolhe o modelo**: usa o padrão configurado em cada CLI. O custo por chamada entra na medição da T46.

## O que fica para o código (T33, T35 a T37)

- `tokens` da `ChamadaIA` fica `None` no Kiro: o painel mostra "não informado" (R11.3).
- A resposta de cada CLI passa pelo mesmo caminho: o provedor extrai o texto da resposta, e o cliente procura o primeiro objeto JSON nele (seção 11 do design).
- Falha: código de saída diferente de zero, tempo limite estourado ou, no Claude, `is_error: true`. No Codex, falta do `agent_message` também conta como falha.
- Nenhuma das três precisou de terminal (TTY), nem perguntou nada.

## A conferir no Windows (na T42)

- `shutil.which("claude")`, `which("codex")` e `which("kiro-cli")` acham o executável (`.exe` ou `.cmd`, conforme a instalação).
- Os mesmos três comandos, com o prompt pela entrada padrão, voltam com código 0 e o mesmo formato.
- Os acentos chegam certos com `encoding="utf-8"`: o console do Windows pode usar outra página de código.
- Se o Kiro CLI não tiver versão para Windows, o design registra isso e o README indica Claude ou Codex no Windows.
