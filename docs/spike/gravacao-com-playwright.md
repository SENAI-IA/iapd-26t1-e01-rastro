# Spike: gravar a visita com Playwright (T58)

Exploração de 13/11/2026 para decidir se o Rastro pode gravar o HAR sozinho, sem o DevTools, e se um robô com travas acha as mesmas bibliotecas que uma pessoa. Base do R24.

**Só o Linux foi conferido.** O Windows fica para a T42 (ver "A conferir no Windows").

## Como foi feito

Tudo fora do repositório, numa pasta temporária, sem instalar nada no sistema:

- **Playwright 1.65** (Node, para o primeiro spike) e **Playwright para Python 1.65.1** (venv separado, para o robô).
- **Alvos:** os contêineres da avaliação (`avaliacao/README.md`), com as mesmas imagens: Juice Shop, WebGoat e Drupal, em `127.0.0.1`.
- **Navegador:** o Chromium baixado pelo Playwright e o Google Chrome 157 já instalado (`--channel chrome`), num display virtual (Xvfb), para não abrir janela na tela.
- **Login:** feito por script no lugar da pessoa (cadastro no WebGoat; link de uso único do `quick-start` no Drupal).
- **Análise:** `python -m rastro analisar --sem-ia --nao-abrir` em cada HAR, comparando com o HAR do Chrome em `avaliacao/`.

## Gravação à mão: `playwright open --save-har`

O comando abre uma janela; a pessoa navega e fecha; o HAR é gravado ao fechar.

| | Juice Shop | WebGoat (cadastro, login e as 3 páginas do gabarito) |
|---|---|---|
| Scripts com conteúdo | 7 de 7 (o HAR do Chrome também tem 7) | 77 de 77 |
| Bibliotecas, sem IA | 0, igual ao HAR do Chrome | **6, 20 achados, nota 9,4: igual ao HAR do Chrome** |
| Site analisado | `127.0.0.1:3000` | `127.0.0.1:8080` |

O WebGoat foi gravado por um script com as mesmas opções de gravação do `open` (`recordHar` com `mode: "minimal"`). O Juice Shop foi gravado com o comando real.

### Formato do HAR do Playwright

O `--save-har` usa `mode: "minimal"` (`coreBundle.js`, `saveHar`). Em relação ao HAR do Chrome:

- **Conteúdo das respostas embutido** (`content: "embed"`, padrão para `.har`). É o que o Rastro precisa para identificar bibliotecas.
- **Sem `log.pages`.** O site analisado sai da primeira resposta HTML (regra de reserva do R01.7) e saiu certo nos três alvos.
- **`startedDateTime` e `time` presentes:** o replay da visita (R22) funciona.
- **`request.cookies` e `response.cookies` vazios, mas os cabeçalhos `Cookie` e `Set-Cookie` ficam.** O Rastro lê o `Set-Cookie`, e as checagens C06 e C08 rodaram no WebGoat (`JSESSIONID` sem HttpOnly). No HAR sanitized do Chrome, elas ficam "não verificadas".
- **O arquivo em disco guarda a sessão** (o valor do `JSESSIONID`). O relatório não traz o valor (conferido no JSON), mas a pessoa precisa saber que o `.har` tem a sessão.
- Quando não há cookie, a checagem diz "exportar o HAR completo inclui as checagens", o que não faz sentido para quem gravou pelo Playwright.

### Encerrar a gravação

- Fechar a última janela grava o HAR (`closeBrowser` no `open`).
- **Ctrl+C no `open` também gravou** o HAR (2,8 MB, Juice Shop).

### Tamanho

| O que | Tamanho |
|---|---|
| `playwright install chromium` (Chromium, headless shell e ffmpeg) | **701 MB** |
| Pacote `playwright` do npm | 19 MB, mais o Node.js |
| Pacote `playwright` do pip, num venv | 185 MB (traz o driver em Node dentro) |
| Com `--channel chrome` ou `msedge` | nenhum navegador baixado: usa o que já está instalado |

**Conclusão:** para um leigo, o caminho é o Playwright para Python com o Chrome ou o Edge da máquina. Assim não precisa de Node.js nem do download de 701 MB.

## Robô com travas

Um script em Python (`sync_playwright`, Chrome instalado, `record_har_mode="minimal"`) que segue os links `<a href>` do próprio site em largura, com as travas:

| Trava | Regra no spike |
|---|---|
| Páginas já vistas | URL normalizada (sem os valores da query; fragmento só se for rota de SPA, com `/`) nunca é visitada duas vezes |
| Páginas | no máximo 20 |
| Tempo | no máximo 3 min |
| Profundidade | no máximo 2 cliques a partir da página inicial |
| Mesmo site | só links do mesmo host e porta |
| Links perigosos | não segue `logout`, `sair`, `delete`, `excluir`, `remove`, `uninstall`, `cron`, `flush`, `reset` nem `token=`, nem arquivos (`.pdf`, `.zip`...) |
| Variedade | no máximo 2 páginas visitadas por família (caminho sem o último trecho) |
| Ação | só navega; nunca clica em botão nem envia formulário |

### Resultado contra o gabarito

| Alvo | Robô | Navegação à mão (HAR do Chrome) |
|---|---|---|
| WebGoat, logado | **6 bibliotecas, 20 achados, nota 9,4** em 8 páginas, parou sozinho ("não há mais links novos") | 6 bibliotecas, 20 achados, nota 9,4 |
| Drupal, logado como admin | **3 bibliotecas** (jQuery, jQuery UI, Underscore), 9 achados, nota 9,4 | 4 bibliotecas: também o CKEditor 4.10.1 |
| Drupal, sem login | 1 biblioteca (jQuery), 5 páginas | não se aplica |

O CKEditor só carrega em `/node/add/article`. O robô chegou a `/node/add` (página 12 de 20), mas o orçamento acabou antes do nível seguinte. Com 40 páginas, a trava de tempo (3 min) disparou antes, por causa de uma página lenta.

### O que o robô ensinou

1. **Sem trava de variedade, o orçamento vai para páginas iguais.** Na primeira rodada do Drupal, 8 das 20 páginas foram `/admin/structure/block/manage/<bloco>`.
2. **A trava de variedade precisa contar só páginas visitadas com sucesso.** Contando na fila, as lições do WebGoat (`#lesson/<nome>`) caíam todas na mesma família, as 2 vagas iam para links que falharam e o robô parava com 1 página.
3. **O login é o gargalo.** Sem login, o Drupal mostrou 1 biblioteca em vez de 3. O robô não preenche formulário, por segurança. A saída é a pessoa entrar antes e o robô seguir com a sessão dela.
4. **Robô genérico não acha a página funda que importa.** A pessoa que conhece o site acha. Daí o modo híbrido: a pessoa entra, o robô varre e a pessoa completa antes de fechar.
5. **A própria página faz pedidos sozinha.** O Drupal mandou um `POST /contextual/render` pelo JavaScript dele, sem clique do robô. Só seguir links não garante que nenhum POST saia.
6. **As travas de páginas e de tempo sempre pararam o robô.** Nenhuma rodada entrou em loop.

### Ctrl+C perdia o HAR

No terminal, o Ctrl+C vai para todo o grupo de processos: Python, driver do Playwright e navegador.

| `launch(...)` | Resultado |
|---|---|
| padrão (`handle_sigint=True`) | o robô parou e disse "HAR gravado", mas **o arquivo não existia**. O Playwright fecha o navegador sozinho no Ctrl+C, antes de o contexto gravar o HAR. |
| `handle_sigint=False` | **HAR gravado** (6 MB, 10 páginas) e analisado normalmente (3 bibliotecas). O `context.close()` ainda levanta "Target page, context or browser has been closed", porque o navegador também recebeu o sinal: precisa ser tratado sem assustar a pessoa. |

O robô trata o Ctrl+C com um `signal.signal(SIGINT, ...)` que só marca o pedido de parada; o laço termina a página atual e fecha o contexto.

**Conferido de novo na T60, com o `rastro gravar` real:** com `handle_sigint=False`, o Ctrl+C mandado a todo o grupo grava o HAR e a análise roda. O driver do Playwright (Node) fica no grupo do terminal e sobrevive ao sinal; o navegador o Playwright já abre fora do grupo. **Armadilha de teste:** com `xvfb-run`, o display virtual fica no mesmo grupo, morre com o Ctrl+C e derruba o navegador, e o HAR se perde. Isso não acontece num desktop de verdade. Para testar, rode o `Xvfb` separado (`setsid Xvfb :77 &` e `DISPLAY=:77`).

## Tempo real

**O Playwright só grava o HAR quando o contexto fecha.** Durante a navegação, o arquivo não existe. Um painel "ao vivo" precisaria ouvir as respostas pelo evento `response` e de um servidor local para o relatório, que hoje é um HTML estático (decisão 05). Fica fora: o progresso no terminal e o replay da visita (R22) cobrem o "ver o rastro".

## A conferir no Windows

- `shutil.which` acha o Chrome ou o Edge pelo `channel`, sem caminho fixo.
- Fechar a janela grava o HAR.
- Ctrl+C no PowerShell e no `cmd` grava o HAR com `handle_sigint=False`.
- `pip install playwright` num venv sem permissão de administrador.

## Decisão que este spike sustenta

- Dá para gravar pelo Rastro com o Playwright para Python, opcional, com o navegador que a pessoa já tem. O leitor do HAR não muda.
- A gravação à mão (T60, T61) já foi validada contra o gabarito. O robô (T62, T63) acha o que está a até dois cliques e precisa da pessoa para o login e para as páginas fundas.
