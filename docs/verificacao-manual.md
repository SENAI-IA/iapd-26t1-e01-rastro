# Verificação manual

Os critérios marcados *(verificação manual)* na [spec](../.kiro/specs/rastro/requirements.md) só se conferem olhando a tela; os demais têm teste automático com o ID no nome (ver [Verificação](../README-TECNICO.md#verificação)).

Gere um relatório com IA e um com `--sem-ia` do mesmo HAR (`avaliacao/webgoat.har`) e siga a tabela. Os comandos usam `python3 -m rastro`; com o comando instalado, `rastro`; no Windows, `py -m rastro`.

"Conferido em" é a data no Linux: visto na tela, no Chromium, nos [prints](prints/) ou numa conferência automatizada com o Playwright. No Windows, nada foi conferido ainda (lista abaixo).

## Roteiro

| # | Passo | Como | Resultado esperado | Requisito | Conferido em |
|---|---|---|---|---|---|
| 1 | Ajuda | `python3 -m rastro --help` e `analisar --help` | Lista `analisar`, `gravar`, `pentest`, `como-usar`, `instalar` e `desinstalar`; no `analisar --help`, `--sem-ia` diz o que se perde na mesma linha | R14.7 | 09/11 (lista de comandos atualizada em 26/11) |
| 2 | Análise com IA | Analisar o HAR com IA | Terminal mostra a pasta, o `relatorio.html` e o resumo de uma linha | R13.1, R13.8 | 09/11 (Kiro) |
| 3 | Análise sem IA | O mesmo HAR com `--sem-ia` | Terminal e topo do relatório avisam que a análise está incompleta; "Encontradas só pela IA" mostra "Não procurado" | R14.5, R14.6 | 09/11 |
| 4 | IA desconhecida | `--ia gpt` | Erro com código 1 listando `kiro, claude, codex` | R14.2 | 09/11 |
| 5 | Offline | Abrir o `relatorio.html` com duplo clique, sem internet | Abre completo, sem requisição externa | R13.5 | 09/11 (0 requisições externas) |
| 6 | Tema e tela estreita | Trocar o tema no topo e estreitar a janela para 400px | Claro e escuro legíveis; em 400px, nada cortado | R13.6 | 09/11 (prints 1 a 3; sem rolagem lateral com tudo aberto, nos dois temas) |
| 7 | Origem do dado | Abrir uma biblioteca e clicar em "Ver a origem" ou na nota de uma falha | Painel lateral com HAR → identificação → aviso → cálculo | R10.2 | 09/11 (print 6) |
| 8 | Glossário | Mouse num termo sublinhado; depois `Tab`; depois toque (celular ou modo de toque do DevTools) | A definição aparece nos três casos | R12.1 | 09/11 (mouse no print 9; `Tab`, `Esc` e toque em 400px) |
| 9 | Task | Em "O que fazer agora", "Abrir task" e "Copiar task"; colar num editor | Título, contexto, o que fazer, critério de aceite e evidências, igual ao `texto_task` do JSON | R09.2 | 09/11 (print 7) |
| 10 | Entrar no foco | "Focar" numa zona | A zona ocupa a largura; barra fina no topo com a zona atual, troca de zona e "Sair do foco" | R15.3 | 09/11 (print 8) |
| 11 | Sair do foco | `Esc` ou "Sair do foco" | Volta ao layout completo, na posição da zona | R15.4 | 09/11 |
| 12 | Foco com janelas | Em foco, abrir a origem, um termo, uma task e, sem IA, o aviso | Tudo continua funcionando | R15.5 | 09/11 (`Esc` fecha a origem e mantém o foco) |
| 13 | Foco por teclado | Passos 10 e 11 só com o teclado, em 400px | Funciona por teclado e em tela estreita | R15.6 | 09/11 (sem rolagem lateral) |
| 14 | Como usar | Clicar em "Como usar" e de volta em "Painel" | Abre no painel; "Como usar" mostra a escolha do jeito de gravar e os passos com ilustração; "Marcar como feito" soma no progresso; os comandos têm "Copiar" | R23.1, R23.5 | 19/11 (print 12) |
| 15 | Tour guiado | "Tour guiado", com "Próximo", "Voltar" e as setas; fechar com `Esc` | Uma parte por vez, com "n de total" e os termos do glossário; só as partes que a análise tem; o foco volta ao botão | R23.2, R23.3, R23.4 | 10/11 (print 11; WebGoat com 11 passos, com Pentest 12, `loja.har` 10, Juice Shop sem IA 9; claro, escuro e 400px) |
| 16 | Movimento reduzido | Ativar "reduzir movimento" e abrir o tour e o "Como usar" | Ilustrações paradas e destaque sem transição | R23.7 | 10/11 (`prefers-reduced-motion`) |
| 17 | Guia sem análise | `python3 -m rastro como-usar` | O navegador abre o relatório sem dados no "Como usar", sem "Tour guiado"; o terminal mostra o caminho do `modelo.html` | R23.1, R23.8 | 10/11 (com dados, o relatório segue abrindo no painel) |
| 18 | Comando de qualquer pasta | `python3 -m rastro instalar`, também com o `.venv` ativo; num terminal novo, em outra pasta, `rastro --help`, `rastro como-usar` e `rastro analisar <caminho>/webgoat.har --sem-ia`; depois `rastro desinstalar` | O comando existe fora do projeto; o guia abre; o relatório é gravado; o `desinstalar` tira o atalho e a linha do PATH | R17.3, R18.1 | 11/11 (zsh, `.venv` ativo, atalho com o `/usr/bin/python3.10`; `desinstalar` limpou o `.zshrc`) |
| 19 | Gravar à mão | `rastro gravar <url>`, navegar e fechar a janela | O Chrome (ou o Edge) abre na URL; ao fechar, o terminal mostra o `visita.har`, o aviso da sessão e roda a análise | R24.1, R24.7, R24.8 | Ctrl+C em 13/11 (Juice Shop, Chrome 157); fechar a janela, a conferir |
| 20 | Gravar com o robô | `rastro gravar <url> --robo`, Enter, esperar e Ctrl+C | Aviso de produção antes do Enter; uma linha por página; o motivo da parada; a janela fica aberta até o Ctrl+C; o HAR só tem o host da URL | R24.10–R24.16 | 13/11 (Juice Shop: 8 páginas; HAR só com `127.0.0.1:3000`) |
| 21 | Gravar sem Playwright | `rastro gravar <url>` num Python sem o Playwright | Erro com `"<python>" -m pip install playwright==1.65.1`, código 1, sem abrir navegador | R24.3 | por teste (`test_r24_3_*`) |
| 22 | Jeitos de gravar no guia | `como-usar`, trocando entre "Gravo no navegador", "O Rastro grava" e "O robô navega" | Cada jeito mostra sua tirinha animada, só os seus passos (8, 5 e 6), o que precisa antes, os problemas e os dados; trocar zera o progresso; com "reduzir movimento", tudo parado; no celular, as opções empilham | R24.17 | 13/11 (Chrome, 1280 e 390 px, claro e escuro) |
| 23 | Andamento no terminal | Uma análise e um `rastro gravar <url>` num terminal; depois a análise com `> saida.txt` | No terminal: etapa girando, tempo correndo, itens contando ("2 de 5") e `ok` por etapa; no `gravar`, o que a pessoa precisa fazer sai em negrito amarelo. No arquivo: só `[n/total] etapa`, sem códigos de controle | R13.10, R24.18, R24.19 | 13/11 (pseudo-terminal de 100 colunas) |

## Pendências do Windows (T42)

Todos os passos do roteiro estão a conferir no Windows, e também:

- Os comandos do Windows nos dois READMEs: `py`, `$env:RASTRO_IA`, `Invoke-Item`, a ativação do `.venv` e o build do frontend.
- Se o `kiro-cli` existe para Windows e se `claude` e `codex` são achados (`.exe` ou `.cmd`). Lista completa em [`clis-de-ia.md`](historico/spike/clis-de-ia.md), "A conferir no Windows".
- Se os acentos chegam certos no terminal e no relatório, inclusive com a pasta do projeto num caminho com acento.
- Se o `py -m rastro instalar` põe o `rastro` no PATH do usuário, se ele roda de outra pasta num terminal novo e se o `rastro desinstalar` apaga o próprio `rastro.cmd` sem erro do cmd (passo 18).
- A pasta padrão `C:\Users\<nome>\Rastro\relatorios` e o nome da pasta do site com `_` no lugar de `:` (ex.: `127.0.0.1_8080`).
- O `rastro gravar`: se o Playwright acha o Chrome ou o Edge pelo `channel`, se fechar a janela e o Ctrl+C (PowerShell e `cmd`) gravam o HAR e se o `pip install --user playwright` funciona sem administrador. Ver [`gravacao-com-playwright.md`](historico/spike/gravacao-com-playwright.md), "A conferir no Windows".
