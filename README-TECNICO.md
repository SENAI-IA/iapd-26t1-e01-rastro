# Rastro — documentação técnica

Rastro lê um arquivo HAR, identifica bibliotecas front-end, cruza versões com GitHub Advisory, OSV, NVD e registro do npm, calcula risco e grava um relatório HTML/JSON. A análise é passiva: o site analisado nunca é acessado.

Este documento é referência para desenvolvimento, manutenção, agentes de IA e revisão técnica. Para instalação e uso sem detalhes de implementação, consulte o [README para usuários](README.md).

> **Status:** funcionando no Linux (fases 0 a 3, OSV e NVD, replay da visita, tour guiado e "Como usar"). A instalação do zero no Windows ainda não foi conferida (T42): os comandos do Windows abaixo seguem a convenção do projeto e estão marcados como **a conferir**. Andamento no [kanban](.kiro/specs/rastro/kanban.md).

![Relatório do WebGoat, gerado com a IA Kiro](docs/prints/01-relatorio-claro.png)

## Navegação técnica

**Começar**

- [Pré-requisitos](#o-que-precisa)
- [Instalação](#instalação)
- [Comando `rastro` de qualquer pasta (opcional)](#comando-rastro-de-qualquer-pasta-opcional)
- [Uso rápido](#uso)

**Usar o Rastro**

- [Gravar o HAR](#1-gravar-o-har)
- [Analisar um HAR](#2-analisar)
- [Abrir o relatório](#3-abrir-o-relatório)
- [Conhecer o relatório](#o-relatório)
- [Resultados](#resultados)

**Verificar e desenvolver**

- [Roteiro de verificação manual](#roteiro-de-verificação-manual)
- [Pendências do Windows](#a-conferir-no-windows-t42)
- [Verificação local](#verificação)
- [Frontend](#frontend-só-para-quem-muda-o-relatório)

**Contexto do projeto**

- [Desenvolvido com IA](#desenvolvido-com-ia)
- [Onde está cada coisa](#onde-está-cada-coisa)
- [Como trabalhamos](#como-trabalhamos)
- [Links](#links)
- [Créditos](#créditos)

## O que precisa

| | Para usar | Para desenvolver |
|---|---|---|
| Python 3.10 ou mais novo | sim | sim |
| Internet (GitHub Advisory, OSV, NVD e registro do npm, só leitura) | sim | não (os testes não acessam a rede) |
| CLI de IA instalada e autenticada: Kiro (`kiro-cli`, padrão), Claude (`claude`) ou Codex (`codex`) | só para a análise com IA | não |
| Node.js | não: o HTML do relatório já vem pronto em `rastro/relatorio/modelo.html` | só para mudar o frontend |
| Playwright para Python 1.65.1 e Chrome ou Edge | só para o `rastro gravar` (opcional) | sim, pelo `requirements-dev.txt` (os testes usam dublê) |

- O Rastro não tem dependência Python obrigatória em produção: não há `pip install` para usar. O comando `rastro` de qualquer pasta é opcional (`python3 -m rastro instalar`).
- A exceção opcional é o `rastro gravar` (R24, decisão 12): ele importa o Playwright só nesse comando e usa o Chrome ou o Edge da máquina. Sem o Playwright, o comando mostra como instalar e para. O `pyproject.toml` declara o extra `gravar`.
- O Rastro não instala nem autentica a CLI de IA. Use a que você já tem; sem nenhuma, rode com `--sem-ia`.
- Nada é instalado no sistema nem pede administrador ou `sudo`. O Rastro só cria ou remove o comando `rastro` quando a pessoa pede (`instalar` e `desinstalar`), e só na pasta do usuário.

## Instalação

Na pasta onde quer o projeto:

| Passo | Linux | Windows (PowerShell) — a conferir (T42) |
|---|---|---|
| 1. Conferir o Python | `python3 --version` | `py --version` |
| 2. Baixar o projeto | `git clone <url-do-repositorio> rastro` | `git clone <url-do-repositorio> rastro` |
| 3. Entrar na pasta | `cd rastro` | `cd rastro` |
| 4. Conferir o Rastro | `python3 -m rastro --help` | `py -m rastro --help` |

- `<url-do-repositorio>` é o endereço do repositório na org SENAI-IA. Sem Git, baixe o ZIP pelo navegador e extraia.
- Passou quando o passo 4 mostra `usage: rastro [-h] comando ...`.
- Os comandos rodam **na raiz do projeto** (a pasta que tem `rastro/`, `README.md` e `README-TECNICO.md`). O HAR pode estar em qualquer lugar. Para rodar de qualquer pasta, veja o comando `rastro`, logo abaixo.
- Para a IA, confira que a CLI responde no terminal antes: `kiro-cli --version`, `claude --version` ou `codex --version`. No Windows ainda não foi conferido se existe `kiro-cli`; se não houver, use `--ia claude`.

### Comando `rastro` de qualquer pasta (opcional)

Para não precisar entrar na pasta do projeto, a pessoa cria o comando `rastro` com o próprio Rastro, uma vez, na raiz do projeto. O `python -m rastro` na raiz continua sendo o caminho garantido.

| Passo | Linux | Windows (PowerShell) — a conferir (T42) |
|---|---|---|
| 1. Criar o comando, na raiz do projeto | `python3 -m rastro instalar` | `py -m rastro instalar` |
| 2. Conferir, num terminal novo e em outra pasta | `rastro --help` | `rastro --help` |
| Remover | `rastro desinstalar` | `rastro desinstalar` |

- O `instalar` grava um atalho marcado (`~/.local/bin/rastro`; no Windows, `%LOCALAPPDATA%\Rastro\bin\rastro.cmd`) que roda `python -m rastro` com a raiz do projeto no `PYTHONPATH`. Se a pasta não estiver no PATH, acrescenta um bloco marcado no `.bashrc`, `.zshrc` ou `.profile`, conforme o `$SHELL` (no Windows, no PATH do usuário, no registro `HKCU\Environment`). Sem pip, sem internet e sem `sudo`.
- O atalho usa o Python do sistema, mesmo com o `.venv` ativo, para não quebrar se o `.venv` for apagado. Como aponta para a pasta do projeto, um `git pull` já vale; mover a pasta pede outro `instalar`.
- O `desinstalar` remove só o atalho com a marca e o bloco marcado do PATH. Um `rastro` que não tem a marca (do pipx, por exemplo) não é sobrescrito nem apagado: o comando para com mensagem clara.
- Quem preferir pode instalar com o pipx (`pipx install .`): o `pyproject.toml` continua declarando o comando `rastro` e os arquivos de dados.
- Com o comando instalado, `rastro` substitui `python3 -m rastro` (Windows: `py -m rastro`) em todos os comandos deste documento.
- O pacote declara o `modelo.html` e os prompts de `rastro/ia/prompts/` como dados, porque o código os lê com `importlib.resources`. Arquivo novo que não seja `.py` dentro de `rastro/` precisa entrar em `[tool.setuptools.package-data]` no `pyproject.toml`; o `tests/test_instalacao.py` confere.

## Uso

Para ver o passo a passo antes de ter um HAR, abra o guia **Como usar** do relatório, sem analisar nada:

| Linux | Windows (PowerShell) — a conferir (T42) |
|---|---|
| `python3 -m rastro como-usar` | `py -m rastro como-usar` |

O comando abre no navegador o relatório sem dados, já na aba "Como usar", e mostra no terminal o caminho do arquivo. Não lê HAR, não acessa a rede e não grava nada. Se o navegador não abrir (num servidor sem tela, por exemplo), abra esse arquivo à mão.

### 1. Gravar o HAR

Pelo DevTools, como abaixo, ou pelo próprio Rastro, com `rastro gravar <url>` (à mão) ou `rastro gravar <url> --robo` (o robô navega pelos links depois do Enter). O passo a passo do `gravar` está no [README](README.md#gravar-pelo-rastro-opcional); o desenho, na seção 18 do design e na decisão 12.


No Chrome ou no Edge, no site que você quer analisar (o seu, ou um que tem autorização para auditar):

1. Abra o DevTools (`F12`) na aba **Rede** (*Network*).
2. Marque **Desativar cache** (*Disable cache*), deixe o filtro em **Todos** (*All*) e recarregue a página, para os scripts virem com o conteúdo. O HAR só leva o que aparece na lista: com o filtro em *Fetch/XHR*, sai sem nenhum script.
3. Navegue pelas páginas que importam.
4. Clique no ícone de download da aba Rede e escolha **Exportar HAR (sanitized)**: sai sem cookies e cabeçalhos de autenticação.

Para testar sem gravar nada, use os HARs da pasta [`avaliacao/`](avaliacao/README.md) (WebGoat, Drupal e Juice Shop).

> A exportação manual no Chrome ainda está sendo conferida (T04, `avaliacao/README.md`): os HARs de `avaliacao/` foram gravados pelo Playwright.

### 2. Analisar

| | Linux | Windows (PowerShell) — a conferir (T42) |
|---|---|---|
| Com IA (Kiro, o padrão) | `python3 -m rastro analisar site.har` | `py -m rastro analisar site.har` |
| Com outra IA | `python3 -m rastro analisar site.har --ia claude` | `py -m rastro analisar site.har --ia claude` |
| Sem IA (análise incompleta) | `python3 -m rastro analisar site.har --sem-ia` | `py -m rastro analisar site.har --sem-ia` |
| Em outra pasta de saída | `python3 -m rastro analisar site.har --saida relatorios` | `py -m rastro analisar site.har --saida relatorios` |
| Escolher a IA para a sessão | `export RASTRO_IA=codex` | `$env:RASTRO_IA = "codex"` |

| Opção ou variável | O que faz |
|---|---|
| `--ia NOME` | `kiro`, `claude` ou `codex`. Sem a opção, vale `RASTRO_IA`; sem as duas, `kiro`. O Codex roda com as opções que tiram dele as ferramentas de comando, mas esse efeito não foi conferido (sem chave de API no grupo): para HAR de terceiros, prefira o Kiro ou o Claude. |
| `--sem-ia` | Não chama a IA: não procura bibliotecas escondidas em bundles e não explica os achados. Nota, prioridade, checagens e plano de ação são os mesmos. |
| `--saida PASTA` | Troca a pasta dos relatórios. Padrão: `~/Rastro/relatorios` no Linux e `C:\Users\<nome>\Rastro\relatorios` no Windows. |
| `GITHUB_TOKEN` (opcional) | Sem token, o GitHub Advisory aceita 60 consultas por hora (uma por biblioteca); com token, 5.000. |
| `NVD_API_KEY` (opcional) | Chave do NVD, usada só para completar o CVSS que faltar. |

Com IA, cada chamada pode levar até 2 minutos. Exemplo real, no Linux, com o HAR do WebGoat e o Kiro (09/11/2026, 2 min 8 s):

```
$ python3 -m rastro analisar avaliacao/webgoat.har
Análise com a IA kiro. Cada chamada à IA pode levar até 2 minutos; o que ela sugere passa pelas travas antes do relatório.

Relatório gravado em: /home/<nome>/Rastro/relatorios/127.0.0.1_8080/2026-11-09_14-04-47
HTML: /home/<nome>/Rastro/relatorios/127.0.0.1_8080/2026-11-09_14-04-47/relatorio.html
JSON: /home/<nome>/Rastro/relatorios/127.0.0.1_8080/2026-11-09_14-04-47/relatorio.json
Resumo: 127.0.0.1:8080 · bibliotecas: 6 (6 com falhas) · achados: 20 · nota máxima: 9,4 · ações: 9 (6 alta, 1 média, 2 baixa, 0 a avaliar)
```

- Cada análise vai para uma pasta nova, `<site>/<AAAA-MM-DD_HH-MM-SS>/`. O Rastro nunca sobrescreve um relatório e nunca altera o HAR.
- Erro (HAR que não existe ou inválido, IA desconhecida, CLI de IA não encontrada, pasta da análise que já existe) encerra com código 1 e a mensagem começa com `rastro: erro:`. Exemplo: `rastro: erro: a CLI da IA kiro (kiro-cli) não foi encontrada no sistema. Escolha outra IA com --ia. Use --sem-ia (...)`.

### 3. Abrir o relatório

Ao fim da análise, o Rastro abre o `relatorio.html` no navegador; com `--nao-abrir`, só grava. Se o navegador não abrir (num servidor sem tela, por exemplo), o Rastro avisa e o caminho fica no terminal. O arquivo abre com duplo clique, offline, sem nenhuma requisição externa. Pelo terminal:

| Linux | Windows (PowerShell) — a conferir (T42) |
|---|---|
| `xdg-open <caminho do relatorio.html>` | `Invoke-Item <caminho do relatorio.html>` |

Na primeira vez, use o botão **Tour guiado**, no topo: ele passa por cada parte da tela. A aba **Como usar** repete, dentro do relatório, o caminho do HAR ao relatório.

O `relatorio.json` tem os mesmos dados, para guardar ou comparar análises.

## O relatório

Prints do relatório do WebGoat (`avaliacao/webgoat.har`), gerados no Linux em 09/11/2026 com o Chromium.

| | |
|---|---|
| ![Tema escuro](docs/prints/02-relatorio-escuro.png) **Tema escuro.** Segue o sistema; o botão no topo troca. | ![Tela de 400px](docs/prints/03-relatorio-400px.png) **Tela de 400px.** Os indicadores viram uma coluna. |
| ![Análise sem IA](docs/prints/04-relatorio-sem-ia.png) **Sem IA.** O aviso fica no topo e "Encontradas só pela IA" mostra "Não procurado". | ![Explicação da IA](docs/prints/05-explicacao-da-ia.png) **Explicação da IA** em cada biblioteca, marcada "Sugerido pela IA: confira antes de usar". |
| ![Origem do dado](docs/prints/06-origem-do-dado.png) **Origem do dado:** HAR → identificação → aviso → cálculo da nota. | ![Task para o board](docs/prints/07-task.png) **Task** em Markdown, pronta para colar no board. |
| ![Modo foco](docs/prints/08-modo-foco.png) **Modo foco** na zona Agir. | ![Glossário](docs/prints/09-glossario.png) **Glossário:** a definição aparece no termo sublinhado. |
| ![Onde a IA entrou](docs/prints/10-onde-a-ia-entrou.png) **Onde a IA entrou:** chamadas, tempo, tokens e travas acionadas. | ![Tour guiado](docs/prints/11-tour-guiado.png) **Tour guiado:** um balão por parte da tela, só com as partes que a análise tem. |
| ![Como usar](docs/prints/12-como-usar.png) **Como usar:** do HAR ao relatório em sete passos, com ilustração e "Marcar como feito". | |

## Resultados

Medido em 09/11/2026 nos três HARs de [`avaliacao/`](avaliacao/README.md), contra o gabarito. Detalhes, travas por análise e como medir de novo em [`avaliacao/resultados.md`](avaliacao/resultados.md).

| Métrica (PRD) | Sem IA | Com IA (Kiro) | Com IA (Claude) |
|---|---|---|---|
| Bibliotecas confirmadas, todas do gabarito | 10 | 11 | 11 |
| Bibliotecas com aviso confirmadas (gabarito: 11) | 10 | 10 | 10 |
| Falhas encontradas (gabarito: 30 válidas) | 30 | 30 | 30 |
| Bibliotecas confirmadas fora do gabarito (falso positivo) | **0** | **0** | **0** |
| Sugestões da IA barradas pelas travas | — | 1 de 2 (trava 3, ancoragem) | 1 de 2 (trava 3, ancoragem) |
| Tempo das 3 análises | 14 s | 3 min 29 s | 2 min 15 s |
| Tokens (13 chamadas) | — | não informado pela CLI | 410 mil (31,5 mil por chamada) |
| Tempo de triagem manual × Rastro | **pendente**: medir com uma pessoa | | |

- A biblioteca que a IA acrescenta é o `@angular/core` do Juice Shop, num bundle sem comentário de versão. A que falta sem IA e com IA é a jQuery UI 1.10.3 do WebGoat, que não está no npm e fica "a confirmar".
- O Codex não foi medido: a chave de API expirou e depois foi removida, e o grupo não tem outra. Com ele, as chamadas falharam e a análise seguiu só com a assinatura.

## Roteiro de verificação manual

Os critérios marcados *(verificação manual)* na spec só se conferem olhando a tela; os demais têm teste automático com o ID no nome (`pytest`). Gere um relatório com IA e um com `--sem-ia` do mesmo HAR e siga a tabela:

| # | Passo | O que deve acontecer | Critério | Linux | Windows |
|---|---|---|---|---|---|
| 1 | Rodar `python3 -m rastro --help` (Windows: `py -m rastro --help`) | Mostra os comandos `analisar` e `como-usar`; no `analisar --help`, `--sem-ia` diz o que se perde na mesma linha | R14.7 | conferido 09/11 | a conferir (T42) |
| 2 | Analisar `avaliacao/webgoat.har` com IA | Terminal mostra a pasta, o `relatorio.html` e o resumo de uma linha | R13.1, R13.8 | conferido 09/11 (Kiro) | a conferir (T42) |
| 3 | Analisar o mesmo HAR com `--sem-ia` | Terminal e topo do relatório avisam que a análise está incompleta; "Encontradas só pela IA" mostra "Não procurado" | R14.5, R14.6 | conferido 09/11 | a conferir (T42) |
| 4 | Rodar com `--ia gpt` | Erro com código 1 listando `kiro, claude, codex` | R14.2 | conferido 09/11 | a conferir (T42) |
| 5 | Abrir o `relatorio.html` com duplo clique, sem internet | Abre completo, sem requisição externa | R13.5 | conferido 09/11 (0 requisições externas no Chromium) | a conferir (T42) |
| 6 | Trocar o tema no botão do topo e estreitar a janela para 400px | Claro e escuro legíveis; em 400px, nada cortado | R13.6 | conferido 09/11 (prints 1 a 3; em 400px, sem rolagem lateral com tudo aberto, nos dois temas) | a conferir (T42) |
| 7 | Abrir uma biblioteca e clicar em "Ver a origem" ou na nota de uma falha | Painel lateral com HAR → identificação → aviso → cálculo | R10.2 | conferido 09/11 (print 6) | a conferir (T42) |
| 8 | Passar o mouse num termo sublinhado; depois chegar nele com `Tab`; depois tocar (celular ou modo de toque do DevTools) | A definição aparece nos três casos | R12.1 | conferido 09/11 (mouse no print 9; `Tab`, `Esc` e toque em 400px no Chromium) | a conferir (T42) |
| 9 | Em "O que fazer agora", clicar em "Abrir task" e em "Copiar task"; colar num editor | Texto com título, contexto, o que fazer, critério de aceite e evidências, igual ao do JSON | R09.2 | conferido 09/11 (print 7; o texto copiado é igual ao `texto_task` do JSON) | a conferir (T42) |
| 10 | Clicar em "Focar" numa zona | A zona ocupa a largura; barra fina no topo com a zona atual, troca de zona e "Sair do foco" | R15.3 | conferido 09/11 (print 8) | a conferir (T42) |
| 11 | Apertar `Esc` ou "Sair do foco" | Volta ao layout completo, na posição da zona | R15.4 | conferido 09/11 (volta com a zona logo abaixo do topo) | a conferir (T42) |
| 12 | Em foco, abrir a origem, um termo do glossário, uma task e, no relatório sem IA, o aviso | Tudo continua funcionando | R15.5 | conferido 09/11 (origem, glossário, task e aviso sem IA; `Esc` fecha a origem e mantém o foco) | a conferir (T42) |
| 13 | Fazer os passos 10 e 11 só com o teclado e em 400px | Funciona por teclado e em tela estreita | R15.6 | conferido 09/11 (só teclado, em 400px, sem rolagem lateral) | a conferir (T42) |
| 14 | Abrir o relatório e clicar em "Como usar" e de volta em "Painel" | Abre no painel; "Como usar" mostra os sete passos com ilustração, "Marcar como feito" soma no progresso e os comandos têm "Copiar" | R23.1, R23.5 | conferido 10/11 (print 12) | a conferir (T42) |
| 15 | Clicar em "Tour guiado" e andar com "Próximo", "Voltar" e as setas; fechar com `Esc` | Destaca uma parte por vez, com "n de total" e os termos do glossário; só as partes que a análise tem; o foco volta ao botão | R23.2, R23.3, R23.4 | conferido 10/11 (print 11; WebGoat com 11 passos, `loja.har` com 10, Juice Shop sem IA com 9; claro, escuro e 400px) | a conferir (T42) |
| 16 | Ativar "reduzir movimento" no sistema e abrir o tour e o "Como usar" | Ilustrações paradas e destaque sem transição | R23.7 | conferido 10/11 (Chromium com `prefers-reduced-motion`) | a conferir (T42) |
| 17 | Rodar `python3 -m rastro como-usar` (Windows: `py -m rastro como-usar`) | O navegador abre o relatório sem dados já no "Como usar", sem o botão "Tour guiado"; o terminal mostra o caminho do `modelo.html` | R23.1, R23.8 | conferido 10/11 (Chromium; com dados, o relatório segue abrindo no painel) | a conferir (T42) |
| 18 | Rodar `python3 -m rastro instalar` (Windows: `py -m rastro instalar`), inclusive com o `.venv` ativo, e, num terminal novo, em outra pasta, rodar `rastro --help`, `rastro como-usar` e `rastro analisar <caminho>/webgoat.har --sem-ia`; depois `rastro desinstalar` | O comando existe fora do projeto; o guia abre; o relatório é gravado completo; o `desinstalar` tira o atalho e a linha do PATH, e o `rastro` some num terminal novo | R17.3, R18.1 | conferido 11/11 (pasta de usuário de teste, com o `.venv` ativo e zsh: atalho com o `/usr/bin/python3.10`, `--help` de outra pasta, `desinstalar` limpou o `.zshrc`) | a conferir (T42) |
| 19 | Rodar `rastro gravar <url>`, navegar e fechar a janela | O Chrome (ou o Edge) abre na URL; ao fechar, o terminal mostra o `visita.har`, o aviso da sessão e roda a análise | R24.1, R24.7, R24.8 | Ctrl+C conferido 13/11 (Juice Shop, Chrome 157, Linux); fechar a janela, a conferir | a conferir (T42) |
| 20 | Rodar `rastro gravar <url> --robo`, apertar Enter, esperar o robô e apertar Ctrl+C | Aviso de produção antes do Enter; uma linha de progresso por página; o motivo da parada; a janela continua aberta até o Ctrl+C; o HAR só tem o host da URL | R24.10–R24.16 | conferido 13/11 (Juice Shop: 8 páginas, parou sem links novos; o HAR só com `127.0.0.1:3000`) | a conferir (T42) |
| 21 | Rodar `rastro gravar <url>` num Python sem o Playwright | Erro com o comando `"<python>" -m pip install playwright==1.65.1`, código 1, sem abrir navegador | R24.3 | conferido por teste (`test_r24_3_*`) | a conferir (T42) |
| 22 | Rodar `python3 -m rastro como-usar` e trocar entre "Gravo no navegador", "O Rastro grava" e "O robô navega" | Cada jeito mostra uma tirinha animada (só anda no cartão escolhido ou com o mouse em cima), só os seus passos (8, 5 e 6), o que precisa antes, os problemas e os dados; trocar zera o progresso; com "reduzir movimento", tudo parado; no celular, as três opções ficam uma embaixo da outra | R24.17 | conferido 13/11 (Chrome, 1280 px e 390 px, claro e escuro, reduzir movimento, sem erro no console) | a conferir (T42) |

"Conferido 09/11" quer dizer: visto na tela, no Chromium, nos prints de `docs/prints/` ou numa conferência automatizada com o Playwright. "A conferir" fica para a pessoa do grupo que seguir este README do zero (revisão da T43) e para a T42, no Windows.

## A conferir no Windows (T42)

- O `rastro gravar` (extensão R24): se o Playwright acha o Chrome ou o Edge pelo `channel`, se fechar a janela grava o HAR, se o Ctrl+C no PowerShell e no `cmd` grava o HAR e se o `pip install --user playwright` funciona sem administrador. Ver `docs/spike/gravacao-com-playwright.md`, "A conferir no Windows".

- Os comandos marcados "a conferir" nas tabelas: `py`, `$env:RASTRO_IA`, `Invoke-Item` e a ativação do `.venv`.
- Se o `kiro-cli` existe para Windows e se `claude` e `codex` são achados (`.exe` ou `.cmd`). A lista completa está em `docs/spike/clis-de-ia.md`, "A conferir no Windows".
- Se os acentos chegam certos no terminal e no relatório.
- Se o `py -m rastro instalar` põe o comando `rastro` no PATH do usuário, se ele roda de outra pasta, num terminal novo, e se o `rastro desinstalar` apaga o próprio `rastro.cmd` sem erro do cmd (passo 18 do roteiro). Pasta do projeto com acento no caminho também.
- A pasta padrão `C:\Users\<nome>\Rastro\relatorios` e o nome da pasta do site com `_` no lugar de `:` (ex.: `127.0.0.1_8080`).

## Verificação

Não há CI: a verificação roda na máquina local, no Linux e no Windows, antes de cada entrega. Precisa só do Python 3.10 ou mais novo. As ferramentas, com versão fixa no `requirements-dev.txt`, ficam no `.venv` do projeto; nada é instalado globalmente.

Na raiz do projeto:

| Passo | Linux | Windows (PowerShell) |
|---|---|---|
| 1. Criar o `.venv` (uma vez) | `python3 -m venv .venv` | `py -m venv .venv` |
| 2. Ativar o `.venv` | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| 3. Instalar as ferramentas (uma vez) | `pip install -r requirements-dev.txt` | `pip install -r requirements-dev.txt` |
| 4. Estilo e erros comuns | `ruff check` | `ruff check` |
| 5. Tipos | `mypy rastro` | `mypy rastro` |
| 6. Testes e cobertura | `pytest --cov=rastro --cov-report=term` | `pytest --cov=rastro --cov-report=term` |

- Se o PowerShell recusar a ativação, libere só para a janela aberta: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
- Passou quando o `ruff` mostra `All checks passed!`, o `mypy` mostra `Success` e o `pytest` termina sem falhas. Os testes não acessam a rede.
- O `requirements-dev.txt` também fixa o setuptools: o `tests/test_instalacao.py` monta o pacote sem rede, e o setuptools do Python do Ubuntu 22.04 é antigo demais para o `pyproject.toml`.
- O resultado de cada sistema fica em `docs/cobertura/linux.md` e `docs/cobertura/windows.md`: data, commit, versões e a saída dos três comandos.

### Cobertura

| Medida (Linux, 10/11/2026, commit b73056d) | Cobertura |
|---|---|
| Regras de negócio (`har`, `identificacao`, `travas`, `fontes`, `risco`, `configuracao`, `acao`, `ia/sanitizacao`) | **99%** (1753 linhas, 3 sem teste) |
| Total do pacote `rastro` | 99% (2450 linhas, 6 sem teste) |

O mínimo é 60% nas regras de negócio, com meta de 80% (R19.1). O relatório HTML, arquivo por arquivo e linha por linha, fica em [`docs/cobertura/html/index.html`](docs/cobertura/html/index.html). Para atualizá-lo, com o `.venv` ativo:

```
pytest --cov=rastro --cov-report=term --cov-report=html:docs/cobertura/html
```

- O número das regras de negócio sai de `coverage report --include="rastro/har/*,rastro/identificacao/*,rastro/travas/*,rastro/fontes/*,rastro/risco/*,rastro/configuracao/*,rastro/acao/*,rastro/ia/sanitizacao.py"`, logo depois do `pytest`.
- O `.gitignore` versionado em `docs/cobertura/html/` não ignora nada e precisa ficar lá: o `pytest-cov`, ao achar a pasta vazia, criaria um `.gitignore` com `*` que esconderia o relatório do Git.

### Frontend (só para quem muda o relatório)

O relatório é React + TypeScript, num único HTML. Mudou algo em `frontend/`, refaça o build e copie o resultado para o pacote Python, no mesmo commit:

| Passo | Linux | Windows (PowerShell) — a conferir (T42) |
|---|---|---|
| 1. Instalar as dependências (uma vez) | `cd frontend` e `npm install` | `cd frontend` e `npm install` |
| 2. Gerar o HTML | `npm run build` | `npm run build` |
| 3. Levar para o pacote | `cp dist/index.html ../rastro/relatorio/modelo.html` | `Copy-Item dist\index.html ..\rastro\relatorio\modelo.html` |

## Desenvolvido com IA

O Rastro foi construído com um agente de IA guiado por arquivos versionados neste repositório. Spec, código e testes foram escritos com o agente, conduzido pelo Paulo task por task; cada commit é revisado por um dos outros cinco membros do grupo, que entra como coautor.

| Arquivo | O que é | Como foi usado |
|---|---|---|
| [`.kiro/specs/rastro/requirements.md`](.kiro/specs/rastro/requirements.md) | Requisitos R01 a R23 em EARS, cada critério com ID | Cada critério vira pelo menos um teste com o ID no nome (`test_r05_2_...`); os que só se veem na tela estão no roteiro acima. |
| [`.kiro/specs/rastro/design.md`](.kiro/specs/rastro/design.md) | Arquitetura, modelos, fórmulas, travas, provedores de IA | O agente lê antes de cada task; o que se decide no meio da task volta para o design no mesmo commit. |
| [`.kiro/specs/rastro/tasks.md`](.kiro/specs/rastro/tasks.md) e [`kanban.md`](.kiro/specs/rastro/kanban.md) | Tasks T01 a T55, com entrega, aceite, arquivos, teste, requisito e revisor; estado de cada uma | Uma task por vez, um commit por task (`feat(risco): ... (T17)`), com o revisor como coautor. O `git log` conta a construção task por task. |
| [`.kiro/steering/`](.kiro/steering/) | Padrões de produto, tecnologia, estrutura, processo, Python e React | Regras que o agente segue em toda task: biblioteca padrão primeiro, núcleo puro, nomes em português, Windows e Linux, nada destrutivo. Mudou um padrão, o steering muda no mesmo commit. |
| [`.kiro/skills/rastro-nova-regra/`](.kiro/skills/rastro-nova-regra/SKILL.md) | Passo a passo para acrescentar checagem, assinatura, fonte de dados, provedor de IA ou trava | Usada nas tasks de regra nova (checagens, assinaturas, OSV, NVD, provedores); o que faltou nela foi corrigido no commit da task. |
| [`docs/decisoes/`](docs/decisoes/) | Uma decisão por arquivo, com contexto e alternativas | O porquê das escolhas (fórmula da nota, IA por CLI, travas contra invenção), em vez de comentário no código. |

E no próprio produto a IA tem papel real, mas não decide sozinha: ela sugere bibliotecas em bundles e explica os achados; travas fixas conferem tudo antes de entrar no relatório, e a nota vem de fórmula. Detalhes em [`docs/decisoes/03-papel-da-ia.md`](docs/decisoes/03-papel-da-ia.md) e [`06-travas-contra-invencao.md`](docs/decisoes/06-travas-contra-invencao.md).

## Onde está cada coisa

| Pasta | Conteúdo |
|---|---|
| `rastro/` | O pacote Python: núcleo (`har`, `identificacao`, `travas`, `fontes`, `risco`, `configuracao`, `acao`), IA (`ia`, `explicacao`), relatório e CLI. |
| `frontend/` | Fonte do relatório HTML (React + TypeScript). O build vai pronto em `rastro/relatorio/modelo.html`. |
| `tests/` | Testes, espelhando `rastro/`, e os dados de teste em `tests/dados/`. |
| `avaliacao/` | HARs do WebGoat, do Drupal e do Juice Shop, o gabarito das bibliotecas de cada um e os resultados medidos com e sem IA. |
| `.kiro/steering/` | Padrões de construção que o agente de IA segue: produto, tecnologia, estrutura, processo, Python e React. |
| `.kiro/specs/rastro/` | Spec do Rastro: requisitos em EARS, design, tasks (com revisor), dependências entre as tasks e kanban. |
| `.kiro/skills/rastro-nova-regra/` | Skill do projeto: passo a passo para acrescentar checagem, assinatura, fonte de dados, provedor de IA ou trava, com teste, cobertura e verificação. |
| `docs/` | Entregáveis: `pitch-inicial.pdf`, `prints/` (telas do relatório), `spike/` (validações da fase 0), `cobertura/` (resultado da verificação em cada sistema e relatório HTML da cobertura) e `decisoes/` (um arquivo por decisão, com contexto, decisão e alternativas). |

## Como trabalhamos

- A spec vem antes do código. Cada task do `tasks.md` é pequena e tem entrega, critério de aceite, arquivos, teste e requisito.
- Um commit por task, direto no `main`, semântico e em pt-BR: `feat(risco): calcular nota de risco pela fórmula fixa (T17)`, com o revisor como coautor. A revisão vem depois do commit; ajuste vira um commit `fix` novo.
- Regras completas em `.kiro/steering/processo.md`.

## Links

- Pitch: [`docs/pitch-inicial.pdf`](docs/pitch-inicial.pdf)
- Telas do relatório: [`docs/prints/`](docs/prints/)

## Créditos

Projeto final do curso de IA aplicada (tema Produtividade do SENAI) · grupo E01 IA SEC.
