# Rastro

Rastro ajuda a descobrir bibliotecas JavaScript e possíveis vulnerabilidades a partir de um arquivo HAR exportado do navegador.

Ele gera um relatório visual com:

- bibliotecas encontradas;
- vulnerabilidades e níveis de risco;
- verificações de configuração;
- explicações e sugestões de ação;
- origem dos dados usados na análise.

A análise é passiva: Rastro lê o HAR e não acessa o site analisado. Se preferir, o [`rastro gravar`](#gravar-pelo-rastro-opcional) abre o navegador e grava a visita por você; aí quem acessa o site é esse navegador. As validações de segurança ativas ficam num comando separado e exigem `--autorizo`.

> **Importante:** use o Rastro somente em sites próprios ou em sites para os quais você tem autorização para auditar.

![Relatório do WebGoat](docs/prints/01-relatorio-claro.png)

## Navegação

- [Antes de começar](#antes-de-começar)
- [Instalar](#instalar)
- [Atualizar e remover](#atualizar-e-remover)
- [Ver o guia sem analisar](#ver-o-guia-sem-analisar)
- [Gravar um arquivo HAR](#gravar-um-arquivo-har)
- [Gravar pelo Rastro (opcional)](#gravar-pelo-rastro-opcional)
- [Validações de segurança ativas (opcional)](#validações-de-segurança-ativas-opcional)
- [Fazer uma análise](#fazer-uma-análise)
- [Abrir o relatório](#abrir-o-relatório)
- [Usar sem IA](#usar-sem-ia)
- [Testar com arquivos de exemplo](#testar-com-arquivos-de-exemplo)
- [Problemas comuns](#problemas-comuns)
- [Documentação técnica](#documentação-técnica)

## Antes de começar

Você precisa de:

- Python 3.10 ou mais novo;
- internet durante a análise, para consultar fontes públicas de vulnerabilidades e pacotes;
- uma CLI de IA instalada e autenticada se quiser análise com IA:
  - Kiro: `kiro-cli`;
  - Claude: `claude`;
  - Codex: `codex`.

Node.js não é necessário para usar o Rastro. O relatório HTML já vem pronto no projeto.

Rastro não instala Python, Node.js nem CLI de IA, e não pede `sudo` nem administrador. Tudo fica na sua pasta de usuário.

## Instalar

### Linux

Rode no terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/SENAI-IA/iapd-26t1-e01-rastro/main/install.sh | bash
```

O instalador confere o Python, baixa o Rastro para `~/.local/share/rastro` e cria o comando `rastro`. Não precisa de Git nem de `sudo`.

Abra um terminal novo e confira:

```bash
rastro --help
```

Para análise com IA, confira também a CLI escolhida:

```bash
kiro-cli --version
# ou
claude --version
# ou
codex --version
```

### Windows

A instalação do zero no Windows ainda está em conferência. Baixe o ZIP do repositório (botão **Code** → **Download ZIP**), extraia a pasta e, dentro dela, rode:

```powershell
py --version
py -m rastro instalar
```

Abra um terminal novo e confira com `rastro --help`.

### Com Git (para quem vai mexer no código)

```bash
git clone https://github.com/SENAI-IA/iapd-26t1-e01-rastro.git rastro
cd rastro
python3 -m rastro instalar
```

O comando `rastro` aponta para essa pasta: um `git pull` já atualiza. Se mudar a pasta de lugar, rode o `instalar` de novo. Sem o `instalar`, use `python3 -m rastro` (Windows: `py -m rastro`) dentro da pasta.

## Atualizar e remover

Para atualizar, rode de novo o mesmo comando `curl` da instalação. Ele troca os arquivos do Rastro pela versão nova; suas gravações e relatórios em `~/Rastro` não mudam.

Para remover:

```bash
rastro desinstalar
```

Ele tira o comando `rastro` e a linha que pôs no PATH, e mostra os comandos para apagar o resto, se você quiser limpar tudo:

```text
Comando rastro removido.
Para limpar tudo, apague também:
  os arquivos do Rastro: rm -rf /home/voce/.local/share/rastro
  suas gravações e relatórios (guarde antes o que quiser manter): rm -rf /home/voce/Rastro
```

O Rastro não apaga essas pastas sozinho: confira e rode você mesmo. Se instalou o Playwright para o `gravar`, remova com `python3 -m pip uninstall playwright`.

## Ver o guia sem analisar

O Rastro possui um guia visual com o passo a passo completo:

```bash
rastro como-usar
```

Esse comando abre o guia no navegador. No alto, escolha como quer gravar a visita (no DevTools, pelo Rastro ou com o robô) e o guia mostra só os passos daquele jeito. Não lê HAR, não consulta a internet e não grava uma análise.

## Gravar um arquivo HAR

No Chrome ou Edge:

1. Abra o site autorizado que deseja analisar.
2. Abra o DevTools com `F12`.
3. Entre na aba **Rede** (*Network*).
4. Marque **Desativar cache** (*Disable cache*) e deixe o filtro em **Todos** (*All*): o HAR só leva o que aparece na lista, e com o filtro em *Fetch/XHR* ele sai sem nenhum script.
5. Recarregue a página e navegue pelas telas importantes.
6. Use o botão de download e escolha **Exportar HAR (sanitized)**.

Use sempre um HAR sanitizado. Ele não deve conter cookies, tokens ou cabeçalhos de autenticação.

Para testar sem gravar um arquivo, use os exemplos em [`avaliacao/`](avaliacao/README.md).

## Gravar pelo Rastro (opcional)

Em vez de usar o DevTools, deixe o Rastro abrir o navegador e gravar por você. No fim, ele já faz a análise.

**Só na primeira vez**, instale o Playwright (precisa do Chrome ou do Edge instalado):

```bash
python3 -m pip install --user playwright==1.65.1
```

No Windows: `py -m pip install --user playwright==1.65.1`. Se der erro, rode o `gravar` assim mesmo: a mensagem mostra o comando certo para o seu computador.

### Você navega

```bash
rastro gravar https://site.com.br
```

1. O navegador abre no site.
2. Navegue pelas páginas que importam.
3. Feche a janela. A análise roda e o relatório abre.

### O robô navega

```bash
rastro gravar https://site.com.br --robo
```

1. O navegador abre no site. Se precisar, faça login.
2. Aperte Enter no terminal. O robô visita os links do site (até 20 páginas ou 3 minutos), sem clicar em botões e sem enviar formulários.
3. Quando ele parar, feche a janela. A análise roda e o relatório abre.

> **Em produção:** não use o robô com um usuário administrador ou com acesso a dados sensíveis. Um link comum pode aprovar, arquivar ou enviar algo. Nesse caso, navegue você mesmo.

Enquanto grava, o terminal mostra o tempo e quantas requisições já foram gravadas.

As opções do `analisar` também valem aqui: `--sem-ia`, `--ia`, `--saida` e `--nao-abrir`.

A gravação fica em `~/Rastro/gravacoes/` e **guarda o seu login no site**. Não compartilhe o arquivo e apague quando não precisar mais. O relatório não traz o login.

## Validações de segurança ativas (opcional)

Se você tem autorização para testar o site, pode executar validações HTTP limitadas no host que aparece no HAR:

```bash
rastro pentest site.har --autorizo
```

O comando seleciona no máximo 20 URLs do mesmo host já presentes no HAR e usa somente `GET`, `HEAD` e `OPTIONS`, sem corpo, cookies, tokens ou cabeçalhos de autenticação. Ele não segue redirecionamentos e não faz payloads, XSS, injeção, CSRF, IDOR, SSRF, fuzzing, brute force ou bypass de autenticação.

O resultado fica em `~/Rastro/pentest/<site>/<data e hora>/pentest.json`. Depois, leve-o ao relatório:

```bash
rastro analisar site.har --pentest <caminho-do-pentest.json>
```

A aba **Segurança ativa** mostra as proteções em três grupos (a corrigir, em ordem e não conferido), com o teste do guia OWASP WSTG que cada uma segue. Ela fica separada da nota, das checagens passivas e do plano de ação. Sem `--autorizo`, o Rastro não lê o HAR nem acessa a rede.

O escopo é a configuração de segurança das respostas do site. Ficam fora do escopo: login e sessão, permissões entre usuários, injeção de código e regras de negócio.

Detalhes e comparação com motores externos estão em [`docs/analise-opcoes-pentest.md`](docs/analise-opcoes-pentest.md).

## Fazer uma análise

### Com IA

Kiro é a IA padrão:

```bash
rastro analisar site.har
```

Escolha outra IA:

```bash
rastro analisar site.har --ia claude
rastro analisar site.har --ia codex
```

Durante a análise, Rastro consulta fontes públicas como GitHub Advisory, OSV, NVD e registro do npm. O site descrito no HAR não é acessado.

Enquanto analisa, o terminal mostra a etapa, quantos itens já foram e o tempo. Com IA, uma etapa pode levar alguns minutos: enquanto o sinal no fim da linha girar, o Rastro está trabalhando.

```text
[1/7] Lendo o HAR · 0:00 · ok
[2/7] Reconhecendo as bibliotecas pelos arquivos · 0:00 · ok
[3/7] Procurando bibliotecas nos bundles com a IA · 2 de 5 · 1:12 /
```

Ao terminar, o terminal mostra os caminhos do relatório HTML e do arquivo JSON:

```text
Relatório gravado em: ...
HTML: .../relatorio.html
JSON: .../relatorio.json
Resumo: ...
```

Cada análise é salva em uma pasta nova. Rastro não sobrescreve relatórios anteriores nem altera o HAR original.

### Escolher a pasta de saída

```bash
rastro analisar site.har --saida meus-relatorios
```

Sem `--saida`, os relatórios ficam em `~/Rastro/relatorios` no Linux.

## Abrir o relatório

Ao fim da análise, o relatório abre sozinho no navegador. Para abrir de novo, use o arquivo `relatorio.html` indicado no terminal. No Linux:

```bash
xdg-open <caminho-do-relatorio.html>
```

Também é possível abrir o arquivo com duplo clique. Para analisar sem abrir o navegador, acrescente `--nao-abrir`. Depois da análise, o relatório funciona offline.

Na primeira visita, use:

- **Tour guiado**, para conhecer as partes da tela;
- **Como usar**, para rever o processo completo;
- **Ver a origem**, para entender de onde veio cada informação.

O `relatorio.json` contém os mesmos dados em formato adequado para guardar, comparar ou processar.

## Usar sem IA

Se você não tiver uma CLI de IA, ainda pode executar a análise:

```bash
rastro analisar site.har --sem-ia
```

Essa análise é incompleta. Ela não procura bibliotecas escondidas em bundles e não gera explicações da IA. As demais etapas continuam funcionando, incluindo consultas, cálculo de risco, checagens e plano de ação.

O relatório e o terminal avisam quando a análise foi feita sem IA.

## Testar com arquivos de exemplo

O projeto inclui HARs sanitizados de três aplicações:

- WebGoat;
- Drupal;
- Juice Shop.

Para analisar o exemplo do WebGoat:

```bash
rastro analisar ~/.local/share/rastro/avaliacao/webgoat.har
```

Para uma execução sem IA:

```bash
rastro analisar ~/.local/share/rastro/avaliacao/webgoat.har --sem-ia
```

Se instalou com Git, os exemplos ficam em `avaliacao/`, dentro da pasta do projeto.

Detalhes dos arquivos e dos resultados ficam em [`avaliacao/README.md`](avaliacao/README.md) e [`avaliacao/resultados.md`](avaliacao/resultados.md).

## Problemas comuns

### `python3: command not found`

Instale Python 3.10 ou mais novo. No Windows, use o comando `py`.

### `rastro: command not found` depois de instalar

Abra um terminal novo: o PATH novo só vale para os terminais abertos depois da instalação. Se continuar, rode o instalador de novo e leia o que ele mostra.

### `já existe um comando rastro` ao instalar

O comando `rastro` foi instalado antes de outro jeito, provavelmente com o pipx. Remova com `python3 -m pipx uninstall rastro` e rode o instalador de novo. O Rastro não apaga um comando que ele não criou.

### `a pasta ... já existe e não foi criada por este instalador`

Já existe uma pasta `~/.local/share/rastro` que não veio do instalador. Ele não mexe nela: mude-a de lugar ou apague-a, e rode o instalador de novo.

### CLI de IA não encontrada

Confira se a CLI está instalada e disponível no terminal. Como alternativa, use `--ia claude`, `--ia codex` ou `--sem-ia`.

### `o Playwright não está instalado` no `gravar`

Rode o comando que a própria mensagem mostra. Ou grave pelo DevTools, como em [Gravar um arquivo HAR](#gravar-um-arquivo-har).

### `nem o Google Chrome nem o Microsoft Edge foram encontrados`

Instale um dos dois. O Rastro usa o navegador do computador e não baixa outro.

### `não foi possível abrir o navegador para gravar a visita`

Feche as janelas do Chrome ou do Edge que estiverem travadas e rode de novo. Se continuar, grave pelo DevTools.

### HAR inválido ou inexistente

Confira o caminho do arquivo e exporte novamente um HAR sanitizado pelo DevTools.

### O navegador não abriu o guia

Abra manualmente o caminho exibido pelo comando `como-usar`.

## Documentação técnica

Desenvolvedores e agentes de IA devem consultar o [README técnico](README-TECNICO.md), que documenta:

- arquitetura e fluxo de análise;
- responsabilidades dos módulos Python;
- fontes externas e interfaces;
- precedência das opções de IA;
- formato e localização da saída;
- testes, cobertura e ferramentas de desenvolvimento;
- build do frontend;
- requisitos, decisões e pendências do projeto.

Mais referências:

- [Requisitos](.kiro/specs/rastro/requirements.md)
- [Design técnico](.kiro/specs/rastro/design.md)
- [Tasks e andamento](.kiro/specs/rastro/tasks.md)
- [Decisões arquiteturais](docs/decisoes/)
- [Telas do relatório](docs/prints/)

## Créditos

Projeto final do curso de IA aplicada, tema Produtividade do SENAI, grupo E01 IA SEC.
