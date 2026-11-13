# Decisão 12: gravar a visita com o Playwright, opcional

Requisitos: R24, R16.1, R17.1 e R20.2. Código: `rastro/captura/` e `rastro/cli.py`. Base: `docs/spike/gravacao-com-playwright.md` (T58).

## Contexto

Para usar o Rastro, o auditor precisa exportar o HAR no DevTools: abrir as ferramentas do navegador, ir à aba Rede, marcar o filtro certo, navegar e exportar. É o passo que mais trava quem não é dev, e o "Como usar" do relatório gasta três passos com ele.

O projeto tinha três regras que impediam o Rastro de fazer isso por conta própria:

- "Nunca o site analisado" (R16.1): o Rastro só lê o HAR.
- Nenhuma dependência Python em produção (`tech.md`).
- Playwright fora do escopo (`product.md`), pensado para a esteira (CI).

O spike de 13/11 (T58) mostrou que o HAR gravado pelo Playwright dá o mesmo resultado que o do Chrome, com o leitor do HAR sem mudança, e que um robô com travas acha as bibliotecas a até dois cliques sem entrar em loop.

## Decisão

- **Comando `rastro gravar <url>`**: abre o navegador, a pessoa navega e fecha a janela, e o Rastro analisa o HAR gravado. Com `--robo`, o Rastro navega sozinho pelos links depois que a pessoa aperta Enter, e a pessoa completa antes de fechar.
- **Playwright para Python, opcional.** Só o `gravar` o importa. Sem ele, o comando diz como instalar, com o caminho do Python que roda o Rastro, e para. O `analisar` continua sem nenhuma dependência. A versão conferida fica fixa no comando sugerido e em `requirements-dev.txt`.
- **O navegador é o da máquina:** Chrome ou, sem ele, Edge (`channel`). O Rastro nunca baixa navegador: o `playwright install chromium` baixou 701 MB no spike.
- **Quem acessa o site é o navegador aberto para a pessoa**, como se ela navegasse. O Rastro em si continua sem fazer requisição ao site (R16.1 ganha essa exceção, escrita).
- **O robô só segue links.** Não clica em botão, não envia formulário, não segue `logout`, `delete`, `token=` e parecidos, nem sai do host. Os limites (20 páginas, 3 min, 2 cliques, 2 por família) param o robô sempre.
- **O HAR guarda a sessão.** O Playwright mantém os cabeçalhos `Cookie` e `Set-Cookie`. O terminal avisa, e o relatório continua sem os valores (R16.4).
- **Ctrl+C grava o HAR.** `handle_sigint=False` e um tratador de `SIGINT` que só pede a parada (sem isso, o HAR se perdia em silêncio).

O que isso custa:

- Mais uma interface (`SessaoDeGravacao`) e um pacote novo (`captura/`).
- O pacote do pip ocupa 185 MB, com o driver em Node dentro.
- O `rastro` instalado pelo `instalar` usa o Python do sistema (decisão 11). O Playwright precisa estar nesse Python. No Ubuntu 24.04, o `pip install --user` é bloqueado (PEP 668), e o caminho é rodar o `gravar` com o `.venv` do projeto ativo.
- O robô não acha página que fica longe da inicial (o CKEditor do Drupal, no spike). A pessoa completa.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Só documentar `npx playwright open --save-har` | Exige Node.js, que quem não é dev não tem, e não liga a gravação à análise. |
| Playwright de Node chamado por `subprocess` | Mesmo problema do Node; o robô teria de ser escrito em JavaScript, fora dos testes do projeto. |
| `playwright install chromium` | 701 MB e um navegador a mais na máquina, contra "não instala nada". |
| Robô sem a pessoa | Sem login, o Drupal mostrou 1 biblioteca em vez de 3; e a página funda que importa só a pessoa conhece. |
| Painel ao vivo no relatório | O Playwright só grava o HAR ao fechar, e o relatório é um HTML estático (decisão 05). O progresso no terminal e o replay da visita (R22) cobrem o "ver o rastro". |
| Instalar o Playwright automaticamente | Contra o R17.2: o Rastro não instala nada por conta própria. |
