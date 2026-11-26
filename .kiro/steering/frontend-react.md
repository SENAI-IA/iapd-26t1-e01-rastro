---
inclusion: fileMatch
fileMatchPattern: "frontend/**"
---

# Frontend React

O relatório abre offline com duplo clique. O React monta a tela a partir do JSON que o Python embute no HTML.

## Componentes

- **Um componente de função por arquivo**, com o CSS ao lado: `Indicador.tsx` + `Indicador.css`.
- **Recebe props, devolve JSX.** Sem classes.
- **Não calcula regra de negócio.** Nota, prioridade e contagens já vêm no JSON.
- **Eventos sobem por props** (`aoIrParaBiblioteca(id)`, `aoAbrirTarefa(acao)`). Só o `App.tsx` e as telas de `telas/` ligam os componentes.
- **Estado só com o React:** `useState` e `useReducer`. O tema escolhido fica no `App` (hook `usarTema`) e desce por props; contexto só quando mais de um componente precisar dele.
- **Componente não exporta tipo nem função para outros:** tipo usado por mais de um componente vai para `telas/tiposDaTela.ts` (tema, aba aberta, origem do dado) ou `relatorio/tiposDoRelatorio.ts` (o JSON); o `id` de elemento que outro componente procura vai para `calculosDeTela/identificadores.ts`.
- **Lógica de tela fora do componente:** hook próprio (`hooks/usarRelogioDoReplay.ts`, `hooks/usarPosicaoDoTour.ts`) e conta de desenho (`calculosDeTela/geometriaDoRadar.ts`, `calculosDeTela/estadoDoRadar.ts`) ficam em `.ts` fora dos componentes. É posição, tempo e tamanho na tela, nunca regra de negócio.
- **Componente pequeno:** até umas 40 linhas de JSX e 25 de lógica, com uma responsabilidade que se diz em uma frase sem "e". Passou disso, divida em componentes com nome (`EtapaNoHar`, `BalaoDoTour`, `RotuloDaFalha`). Subcomponente pode usar o CSS do componente pai quando as classes já estão lá.
- **Comportamento repetido tem um lugar só:** janela modal com `usarJanelaModal` (abre com `showModal`, fecha no Esc, no botão e no clique fora), movimento reduzido com `prefereMenosMovimento()` (`calculosDeTela/movimento.ts`), rolagem abaixo do cabeçalho fixo com `rolarAteOElemento` (`calculosDeTela/rolagem.ts`) e espera pelo próximo quadro com `depoisDeDesenhar` (`calculosDeTela/desenho.ts`). Não reescreva isso dentro do componente.
- **Formatação de apresentação** (nota com vírgula, data, plural com `comPlural`) em `formatacao/formato.ts`, com `Intl` em pt-BR. Formatar não é calcular: nada de regra de negócio ali.
- **Tipos do JSON num único `relatorio/tiposDoRelatorio.ts`**, espelhando os modelos do Python. Mudou o JSON, muda o `tiposDoRelatorio.ts` no mesmo commit.
- **Tokens em português** (`--cor-destaque`, `--fonte-mono`, `--raio`) em `estilos/tokens.css`. O tema segue o sistema; `data-tema="claro"` ou `"escuro"` no `<html>` força um deles.
- Mesmas regras de legibilidade do Python: nomes em português, funções curtas, sem comentários.
- **Caminho plano, sem escada de blocos** (`npm run conferir`, que também roda no `npm run build`: `frontend/conferirAninhamento.mjs` barra função, arrow, método ou componente com mais de dois níveis de bloco aninhado; `if`, `for`, `while`, `switch`, `try` e o callback de `forEach`/`map`/`filter`/`reduce`/`some`/`every`/`find` passado direto contam, `else if` não soma, função interna recomeça e JSX não conta).
  - Saída cedo: o caso especial sai no começo e o caminho normal segue sem recuo; em componente, a lista vazia é um `return` antes do JSX principal (`if (acoes.length === 0) { return …; }` em `PlanoDeAcao`), nunca um ternário no meio do JSX.
  - Tabela: `if`/`else if` ou `switch` que só escolhe um valor (texto, ícone, classe, componente) vira objeto constante com nome tipado como `Record<Chave, Valor>` (`APARENCIA_DO_METODO[metodo]` em `SeloDoMetodo`, `COMO_CONFIRMAR_PELA_TRAVA[trava] ?? comoConfirmarQualquerTrava`).
  - Função por item: laço com decisão chama uma função com nome que diz o que cada volta faz (`passos.flatMap((passo, ordem) => chegadasDoPasso(passo, ordem, bibliotecas))`, depois `.filter(ehAPrimeiraChegada)`).
  - Ternário: nunca encadeado nem um dentro do outro no JSX; `&&` só para mostrar ou não um elemento no JSX, nunca como comando (aí vira `if`).
- **Nomes que se leem de primeira:** por extenso, sem letra solta nem abreviação (`evento`, `indice`, nunca `e`, `i`, `idx`). Componente e tipo nunca têm o mesmo nome, para não precisar de `import { X as Y }`: o tipo descreve o dado (`DescricaoDaZona`, `DescricaoDoPasso`, `ChamadaDaIA`) e o componente diz o que desenha (`ZonaDoPainel`, `PassoDoGuia`, `ItemDaChamadaDaIA`). Lista e item seguem "De/Da/Do": `ListaDeFalhas` e `ItemDaFalha`. A classe CSS segue o nome do componente (`ItemDaFalha` → `item-da-falha`). Siglas do domínio ficam (IA, HAR, CVE, CVSS, EPSS, GHSA, URL, npm, CSP, HSTS, CORS, WSTG, OWASP, JS, CSS, HTML, API, F12), assim como as convenções do React (`Props`, `children`, `setX`, `useRef`, `useEffect`). As chaves do JSON (`texto_task`, `porque`, `duracao_s`…) não mudam: são o contrato com o Python.

## Pastas

Tudo em `frontend/src/`. Cada `.tsx` fica com o seu `.css` ao lado.

- `main.tsx`, `App.tsx`, `App.css`: ponto de entrada e a troca de abas; o `App` guarda o estado da página (aba aberta, foco, tema, janelas abertas) e escolhe a tela.
- `telas/`: a tela "Painel" (`TelaDoPainel`: cabeçalho da análise e zonas) e os tipos que o `App` passa entre as telas (`tiposDaTela.ts`).
- `estilos/`: CSS global da página (tokens, base e fontes embutidas).
- `assets/`: logos e arquivos de fonte usados pelo CSS e pelo favicon.
- `relatorio/`: leitura do JSON embutido no HTML (`lerRelatorioSemValidar`: confia no JSON que o Python gerou, sem conferir campo a campo) e os tipos que espelham esse JSON.
- `conteudo/`: textos fixos da tela (glossário, zonas, passos do tour e do guia, linhas dos terminais desenhados no guia, descrições e grupos do pentest).
- `moldura/`: o que envolve as zonas (barras do topo, aviso de limitações, cabeçalho da análise e a caixa de cada zona).
- `zonas/rastreado/`, `zonas/agir/`, `zonas/detalhes/`: os componentes de cada zona do painel, um por pasta.
- `segurancaAtiva/`: a aba "Segurança ativa" (o resultado do pentest); o agrupamento das validações por categoria fica em `agruparValidacoes.ts`.
- `janelas/`: o que abre por cima da tela (painel da origem do dado e tour guiado). A janela da tarefa (`JanelaDaTarefa`) fica em `zonas/agir/`, junto do plano de ação.
- `guia/`: a tela "Como usar".
- `guia/desenhos/`: os desenhos SVG do guia, um componente por arquivo: `pecas/` (peças usadas pelas ilustrações dos passos e pelas animações dos modos: `Robo`, `Cursor`, `Janela`, `MenuDeLinks`, `MolduraDeTerminal` e o `TerminalQueDigita`, que desenha as linhas de `conteudo/terminaisDoGuia.ts`), `passos/` (um desenho por ilustração de passo) e `modos/` (as miniaturas de cada modo de uso).
- `basicos/`: peças pequenas usadas em várias telas (ícone, selos, termo com a sua `DicaDoTermo`, texto com negrito e código).
- `hooks/`: hooks próprios (`usar…`): tempo e tamanho na tela, tema, modo foco, janela modal, posição do tour, passos feitos do guia e cópia de texto.
- `calculosDeTela/`: contas de posição e desenho (radar, replay, tour, linhas do terminal), rolagem, movimento reduzido, `semRepetir` e os `id`s dos elementos, sem JSX.
- `formatacao/`: formatação de números, datas e plurais para exibir.

## Organização da tela

1. **Indicadores:** risco do site, bibliotecas vulneráveis, encontradas só pela IA, primeira ação.
2. **Rastreado:** replay da visita, gravidade × chance de exploração, plano de correção, onde a IA entrou.
3. **Agir:** "O que fazer agora", com cada ação (`ItemDoPlanoDeAcao`), o porquê, o impacto, quem resolve, "Como verificar" e "Abrir task", que abre a `JanelaDaTarefa`.
4. **Detalhes:** bibliotecas e checagens.

Clique em qualquer dado abre a origem dele num painel lateral (`PainelOrigemDoDado`, um `<dialog>` modal nativo aberto pelo `usarJanelaModal`: Esc, foco preso e devolvido sem código próprio). O painel só mostra o que o JSON traz: a conta da nota é `nota.conta`, nunca refeita no frontend.

- **Modo foco:** botão "Focar" em cada zona (Rastreado, Agir, Detalhes). O layout completo é o padrão; o foco é só um estado no hook `usarModoFoco` (`zonaEmFoco`, com `entrarNoFoco` e `sairDoFoco`, que volta a rolar até a zona), usado pelo `App`, com `BarraDeFoco` no topo e Esc para sair. A `TelaDoPainel` embrulha cada zona numa `ZonaDoPainel` (nome e "Focar"); as zonas ficam em `conteudo/zonas.ts`. Nenhum componente de zona sabe que está em foco.
- **Tour guiado e Como usar:** a `BarraSuperior` troca entre "Painel", "Segurança ativa" quando há resultado do pentest e "Como usar" (estado `abaAtual` no `App`, do tipo `Aba`) e abre o `TourGuiado`. A posição do destaque e do balão (`BalaoDoTour`) vem do hook `usarPosicaoDoTour`. Os passos do tour ficam em `conteudo/tour.ts`, cada um com o seletor de uma classe que já existe na tela: o tour só mostra os passos cujo elemento existe, então mudar a classe de um bloco pede a mesma mudança ali. O passo da segurança ativa só aparece quando a aba foi gerada. Os passos do guia ficam em `conteudo/guia.ts`, com os comandos do README, incluindo a execução opcional do pentest autorizado.
- **Análise incompleta:** `AvisoDeLimitacoes` no topo, sempre visível, quando o JSON traz `limitacoes` (com ou sem IA). Fica presa junto da `BarraSuperior` num único bloco fixo (`app__cabecalho-fixo`, no `App.css`, ref `cabecalhoFixo` no `App`), para as duas não se sobreporem. Quem rola a página desconta a altura desse bloco, que o `App` mede e passa por props (`cabecalhoFixo`): nenhum componente procura `.app__cabecalho-fixo` por conta própria. O indicador "encontradas só pela IA" mostra "não procurado", nunca zero.
- **Pentest opcional:** `BarraSuperior` mostra a aba "Segurança ativa" só quando o JSON traz `pentest`; `PainelDaSegurancaAtiva` e `ItemDaSegurancaAtiva` exibem o resultado ativo separado das zonas, da nota e do plano, agrupado por `segurancaAtiva/agruparValidacoes.ts`. O JSON só chega ao frontend depois de ser produzido pelo comando `pentest --autorizo`.
- **A confirmar:** bibliotecas barradas pelas travas aparecem numa lista separada (`ListaAConfirmar`), com a trava que falhou, o motivo e como conferir à mão. O "como conferir" é texto fixo por nome de trava, em `zonas/detalhes/ComoConfirmarATrava.tsx`: trava nova que manda para "a confirmar" ganha o seu caso ali.
- **Detalhes recolhidos:** biblioteca e checagem abrem fechadas (`<details>`); o resumo mostra o estado com selo (ícone + texto) e o corpo traz evidência e detalhe. Selo de estado só aparece quando o JSON traz o estado; o frontend não deduz estado.

## Identidade visual

- **Cores só por tokens** em `estilos/tokens.css`, com tema claro e escuro. Nenhuma cor literal em componente.
- Paleta petróleo (`#0F5F7A` claro / `#5BB9D4` escuro); violeta só para IA; vermelho, laranja e verde só para estado.
- Cantos retos: 3 a 4px.
- Fontes: IBM Plex Sans (texto), IBM Plex Sans Condensed (títulos e números), IBM Plex Mono (código e dados). O relatório abre offline: as fontes vão embutidas em woff2 (`src/estilos/fontes.css` e `src/assets/fontes/`, subconjunto latin, só os pesos usados, licença OFL ao lado); nada de Google Fonts no build. Peso novo só se a tela usar: um arquivo e um `@font-face` a mais.
- Ícones em traço. Logo: quadrado com dois pontos de rastro até um X.
- Favicon é o logo (`frontend/src/assets/logo-claro.svg` e `logo-escuro.svg`, copiados da identidade visual), embutido no HTML do build pelo `vite.config.ts` (o Vite não embute `<link rel="icon">` sozinho).

## UX e acessibilidade

- Quem usa não é especialista: termos técnicos com explicação ao passar o mouse, focar ou tocar. A definição fica só em `src/conteudo/glossario.ts`; na tela, `<Termo nome="…">` (nunca dentro de botão ou link). Termo novo: uma linha no glossário.
- Estado nunca só por cor: sempre com ícone e texto.
- Foco visível, navegação por teclado, `prefers-reduced-motion` respeitado.
- Funciona a partir de 400px de largura, sem rolagem lateral.
- Animação só para orientar: entrada dos blocos, reordenação, abertura de painéis. Há duas exceções. O replay da visita (`ReplayDaVisita`) é a única animação contínua do painel: para no fim, tem pausa e com `prefers-reduced-motion` já abre parada no fim. As ilustrações do guia "Como usar" (`IlustracaoDoGuia` e `AnimacaoDoModo`, com os desenhos em `guia/desenhos/`) repetem, para mostrar o gesto de cada passo, e ficam paradas com `prefers-reduced-motion`.
