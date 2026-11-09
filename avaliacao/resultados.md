# Resultados da avaliação (T46)

As métricas do PRD medidas nos três HARs desta pasta, contra o `gabarito.json`. Rodada de 09/11/2026, no Linux, commit 7e4dd8f, com o GitHub Advisory, o OSV, o NVD e o registro do npm de verdade (sem `GITHUB_TOKEN`).

> **Rodada parcial.** Falta o tempo de triagem manual, que só se mede com uma pessoa (ver "Tempo de triagem"). A T46 fecha quando ele chegar.

## Como foi medido

```
python3 -m rastro analisar avaliacao/<alvo>.har --sem-ia --saida <pasta fora do repo>
python3 -m rastro analisar avaliacao/<alvo>.har --ia kiro --saida <pasta fora do repo>
python3 -m rastro analisar avaliacao/<alvo>.har --ia claude --saida <pasta fora do repo>
python3 -m rastro analisar avaliacao/<alvo>.har --ia codex --saida <pasta fora do repo>
```

Os números saem do `relatorio.json` de cada análise: `bibliotecas`, `a_confirmar`, `achados`, `ia.chamadas` (tempo e tokens de cada chamada), `ia.com_e_sem_ia`, `ia.tokens_total`, `ia.travas_acionadas` e `analise.duracao_s`. Cada biblioteca confirmada foi conferida contra o gabarito por pacote e versão.

| CLI | Versão | Modelo |
|---|---|---|
| Kiro | `kiro-cli 2.31.1` | o padrão da CLI |
| Claude | `claude 2.1.319` (Claude Code) | o padrão da CLI |
| Codex | `codex-cli 0.166.0` | não rodou: a chave de API expirou e foi removida (ver "Codex") |

## Confiança: falso positivo confirmado

**Zero.** Em 6 análises com IA (Kiro e Claude nos três HARs), 2 com o Codex falhando e 3 sem IA, nenhuma biblioteca foi confirmada fora do gabarito, e nenhum aviso apareceu fora do gabarito.

| | WebGoat | Drupal | Juice Shop |
|---|---|---|---|
| Bibliotecas confirmadas fora do gabarito | 0 | 0 | 0 |
| Avisos fora do gabarito | 0 | 0 | 0 |

## Valor da IA: bibliotecas e falhas com e sem IA

| Alvo | No gabarito | Sem IA | Com IA (Kiro) | Com IA (Claude) |
|---|---|---|---|---|
| WebGoat | 7 bibliotecas com aviso, 20 falhas válidas | 6 bibliotecas, 20 falhas | 6 bibliotecas, 20 falhas | 6 bibliotecas, 20 falhas |
| Drupal | 4 bibliotecas com aviso, 10 falhas válidas | 4 bibliotecas, 10 falhas | 4 bibliotecas, 10 falhas | 4 bibliotecas, 10 falhas |
| Juice Shop | nenhuma com aviso | 0 bibliotecas | **1 biblioteca** (`@angular/core` 22.2.2), 0 falhas | **1 biblioteca** (`@angular/core` 22.2.2), 0 falhas |
| **Total** | 11 bibliotecas com aviso, 30 falhas | **10 confirmadas (10 com aviso), 30 falhas** | **11 confirmadas (10 com aviso), 30 falhas** | **11 confirmadas (10 com aviso), 30 falhas** |

- **Falhas:** as 30 falhas válidas do gabarito, todas encontradas, com e sem IA. O gabarito lista 36 pares biblioteca × aviso para essas bibliotecas; 6 deles são de 3 GHSA que o próprio GitHub marcou como duplicados ou retirados (`GHSA-257q-pv89-v3xv` e `GHSA-wv67-q8rr-grjp` do jQuery, `GHSA-9mvj-f7w8-pvh2` do Bootstrap), e o Rastro, com razão, não os traz.
- **A biblioteca que falta no WebGoat** é a jQuery UI 1.10.3: achada pela assinatura, mas não publicada no npm, por isso fica em "a confirmar" pela trava 4 (com IA e sem IA). Os 6 avisos dela não entram na nota. É o ponto "A decidir: trava 4 nas assinaturas" do `README.md` desta pasta.
- **O que a IA acrescentou:** no Juice Shop, um bundle Angular sem comentário de licença, a assinatura não acha nada e a IA acha o `@angular/core` 22.2.2, confirmado no código publicado no npm. Ele não tem aviso hoje, então não muda a nota. No WebGoat e no Drupal, todas as bibliotecas com aviso já vinham por assinatura.
- **Explicações:** com IA, as 10 bibliotecas com falhas (6 do WebGoat, 4 do Drupal) ganharam explicação da IA, e nenhuma foi barrada pelas travas. Sem IA, o relatório mostra só o resumo do aviso.
- **Fora do alcance, como esperado no gabarito:** as 14 bibliotecas com método `nenhum` (2 do WebGoat, 5 do Drupal, 7 do Juice Shop), sem assinatura e sem trecho com versão. Nenhuma tem aviso.

## Quantas sugestões cada trava barrou

Sugestões da IA (identificação em bundles e explicações), por análise:

| Trava | O que confere | Kiro | Claude |
|---|---|---|---|
| 1. Formato | resposta no formato pedido | 0 | 0 |
| 2. Trecho real | o trecho citado está no código enviado | 0 | 0 |
| 3. Ancoragem | a versão está no trecho citado | **1** (`jquery-form` 3.51.0, WebGoat) | **1** (`jquery-form` 3.51.0, WebGoat) |
| 4. Pacote existe | pacote e versão publicados no npm | 0 | 0 |
| 5. Código confere | o trecho bate com o código publicado | 0 | 0 |
| Explicação sem fato novo | a explicação só usa o que veio do aviso | 0 de 10 | 0 de 10 |
| **Sugestões confirmadas / barradas** | | 1 / 1 | 1 / 1 |

- A IA sugeriu 2 bibliotecas por provedor: o `@angular/core` 22.2.2 (confirmado) e o `jquery-form` 3.51.0 (barrado). O jQuery Form 3.51.0 está mesmo no WebGoat, mas a versão não aparece no trecho enviado, e ele nunca foi publicado no npm: se passasse da trava 3, a trava 4 o barraria.
- Fora da IA, as travas também rodam sem IA: a trava 4 barrou a jQuery UI 1.10.3 (assinatura), e a trava 6 (faixa conferida) registrava 5 faixas que não valem para a versão no WebGoat (4 do Bootstrap 3.1.1 e 1 do jQuery 2.1.4), embora esses 5 avisos continuassem no relatório, porque outra faixa do mesmo aviso cobre a versão. Desde o commit 1dc4d05, a trava 6 só registra o aviso quando nenhuma faixa dele vale; os números de bibliotecas e falhas não mudam.

## Custo da IA: tempo e tokens por provedor

| Alvo | Sem IA | Kiro | Claude |
|---|---|---|---|
| WebGoat (1 identificação + 6 explicações) | 8,2 s | 108,2 s (IA: 102,4 s) | 73,7 s (IA: 63,9 s) · 221.175 tokens |
| Drupal (4 explicações) | 5,7 s | 66,9 s (IA: 62,2 s) | 41,4 s (IA: 36,1 s) · 126.377 tokens |
| Juice Shop (2 identificações) | 0,4 s | 33,5 s (IA: 31,2 s) | 19,6 s (IA: 17,3 s) · 62.474 tokens |
| **Total, 13 chamadas** | **14,3 s** | **208,6 s** (16 s por chamada) | **134,7 s** (9 s por chamada) · **410.026 tokens** (31.540 por chamada) |

- O tempo é o `analise.duracao_s`; entre parênteses, a soma do `duracao_s` das chamadas à IA. Sem IA, quase todo o tempo é a consulta às fontes.
- **Kiro:** a CLI não informa tokens (`tokens_total: null`, R11.2), só créditos, que o Rastro não lê.
- **Claude:** cada chamada custa de 30,5 mil a 32,5 mil tokens. Quase tudo é o prompt de sistema da própria CLI (spike T02); o trecho e o aviso enviados pelo Rastro são uma parte pequena.
- As 13 chamadas de cada provedor responderam, sem nenhuma falha.

## Codex

Não medido. A CLI está instalada, mas a chave de API da máquina expirou: `codex exec` responde `401 Unauthorized ... expired_secret_key`. O Rastro rodou o Juice Shop e o Drupal com `--ia codex` mesmo assim: as 6 chamadas falharam (`a CLI do Codex terminou com código de saída 1`, registrado em `ia.chamadas`), a análise terminou com código 0 e o resultado foi o da assinatura (Juice Shop sem bibliotecas; Drupal com as 4 e o resumo do aviso no lugar da explicação). Na época, o relatório não avisava; desde o commit 061f1b1, o terminal e a faixa do topo dizem quantas chamadas falharam e o que ficou sem IA. Depois a chave foi removida e o grupo não tem outra, então o Codex fica fora da medição. Pelo mesmo motivo, não foi conferido que as opções `--disable shell_tool --disable unified_exec` (code review, commit d803278) tiram da IA as ferramentas de comando: a CLI as aceita, mas o efeito ficou sem teste (`docs/spike/clis-de-ia.md`).

## Tempo de triagem

| | WebGoat |
|---|---|
| Manual (uma pessoa, do HAR à lista do que corrigir) | **pendente**: medir com uma pessoa |
| Rastro sem IA | 8,2 s |
| Rastro com IA | 73,7 s (Claude) a 108,2 s (Kiro) |

O número manual entra aqui, no README e no pitch quando for medido, com quem mediu e como.
