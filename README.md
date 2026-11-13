# Rastro

Rastro ajuda a descobrir bibliotecas JavaScript e possíveis vulnerabilidades a partir de um arquivo HAR exportado do navegador.

Ele gera um relatório visual com:

- bibliotecas encontradas;
- vulnerabilidades e níveis de risco;
- verificações de configuração;
- explicações e sugestões de ação;
- origem dos dados usados na análise.

A análise é passiva: Rastro lê o HAR e não acessa o site analisado.

> **Importante:** use o Rastro somente em sites próprios ou em sites para os quais você tem autorização para auditar.

![Relatório do WebGoat](docs/prints/01-relatorio-claro.png)

## Navegação

- [Antes de começar](#antes-de-começar)
- [Instalar](#instalar)
- [Usar de qualquer pasta (opcional)](#usar-de-qualquer-pasta-opcional)
- [Ver o guia sem analisar](#ver-o-guia-sem-analisar)
- [Gravar um arquivo HAR](#gravar-um-arquivo-har)
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

Rastro não instala Python, Node.js nem CLI de IA, e não pede `sudo` nem administrador. O comando `rastro` opcional só é criado se você pedir, e fica na sua pasta de usuário.

## Instalar

### Linux

Na pasta onde deseja guardar o projeto:

```bash
git clone <url-do-repositorio> rastro
cd rastro
python3 --version
python3 -m rastro --help
```

Troque `<url-do-repositorio>` pelo endereço do repositório. Se não usar Git, baixe o ZIP e extraia a pasta.

O último comando confirma que o Rastro está pronto. Para análise com IA, confira também a CLI escolhida:

```bash
kiro-cli --version
# ou
claude --version
# ou
codex --version
```

### Windows

A instalação do zero no Windows ainda está em conferência. Os comandos esperados são:

```powershell
git clone <url-do-repositorio> rastro
cd rastro
py --version
py -m rastro --help
```

## Usar de qualquer pasta (opcional)

Para digitar só `rastro` em qualquer pasta, sem entrar na pasta do projeto:

1. Na pasta do projeto, rode uma vez:

   ```bash
   python3 -m rastro instalar
   ```

   No Windows: `py -m rastro instalar` (a conferir).

2. Feche o terminal e abra outro.
3. Confira: `rastro --help`

Pronto. Agora, nos exemplos abaixo, troque `python3 -m rastro` por `rastro`.

Para remover: `rastro desinstalar`. Se mudar a pasta do projeto de lugar, rode o passo 1 de novo.

## Ver o guia sem analisar

O Rastro possui um guia visual com o passo a passo completo:

```bash
python3 -m rastro como-usar
```

No Windows:

```powershell
py -m rastro como-usar
```

Esse comando abre o guia no navegador. Não lê HAR, não consulta a internet e não grava uma análise.

## Gravar um arquivo HAR

No Chrome ou Edge:

1. Abra o site autorizado que deseja analisar.
2. Abra o DevTools com `F12`.
3. Entre na aba **Rede** (*Network*).
4. Marque **Desativar cache** (*Disable cache*).
5. Recarregue a página e navegue pelas telas importantes.
6. Use o botão de download e escolha **Exportar HAR (sanitized)**.

Use sempre um HAR sanitizado. Ele não deve conter cookies, tokens ou cabeçalhos de autenticação.

Para testar sem gravar um arquivo, use os exemplos em [`avaliacao/`](avaliacao/README.md).

## Fazer uma análise

Execute o comando na raiz do projeto ou, com o [comando `rastro` instalado](#usar-de-qualquer-pasta-opcional), em qualquer pasta.

### Com IA

Kiro é a IA padrão:

```bash
python3 -m rastro analisar site.har
```

Escolha outra IA:

```bash
python3 -m rastro analisar site.har --ia claude
python3 -m rastro analisar site.har --ia codex
```

No Windows, troque `python3` por `py`.

Durante a análise, Rastro consulta fontes públicas como GitHub Advisory, OSV, NVD e registro do npm. O site descrito no HAR não é acessado.

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
python3 -m rastro analisar site.har --saida meus-relatorios
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
python3 -m rastro analisar site.har --sem-ia
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
python3 -m rastro analisar avaliacao/webgoat.har
```

Para uma execução sem IA:

```bash
python3 -m rastro analisar avaliacao/webgoat.har --sem-ia
```

Detalhes dos arquivos e dos resultados ficam em [`avaliacao/README.md`](avaliacao/README.md) e [`avaliacao/resultados.md`](avaliacao/resultados.md).

## Problemas comuns

### `python3: command not found`

Instale Python 3.10 ou mais novo. No Windows, use o comando `py`.

### `rastro: command not found` depois do `instalar`

Abra um terminal novo: o PATH novo só vale para os terminais abertos depois do `instalar`. Se continuar, rode `python3 -m rastro instalar` (Windows: `py -m rastro instalar`) de novo na pasta do projeto e leia o que ele mostra. Enquanto isso, `python3 -m rastro` na pasta do projeto continua funcionando.

### `já existe um comando rastro` ao rodar o `instalar`

O comando `rastro` foi instalado antes de outro jeito, provavelmente com o pipx. Remova com `python3 -m pipx uninstall rastro` e rode `python3 -m rastro instalar` de novo. O Rastro não apaga um comando que ele não criou.

### CLI de IA não encontrada

Confira se a CLI está instalada e disponível no terminal. Como alternativa, use `--ia claude`, `--ia codex` ou `--sem-ia`.

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
