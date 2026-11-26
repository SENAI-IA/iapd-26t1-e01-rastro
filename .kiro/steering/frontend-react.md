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
- **Eventos sobem por props** (`aoClicarFalha(id)`). Só o `App.tsx` e as telas de `telas/` ligam os componentes.
- **Estado só com o React:** `useState` e `useReducer`. O tema escolhido fica no `App` (hook `usarTema`) e desce por props; contexto só quando mais de um componente precisar dele.
- **Componente não exporta tipo nem função para outros:** tipo usado por mais de um componente vai para `telas/tiposDaTela.ts` (tema, tela aberta, origem do dado) ou `relatorio/tiposDoRelatorio.ts` (o JSON); o `id` de elemento que outro componente procura vai para `calculosDeTela/identificadores.ts`.
- **Lógica de tela fora do componente:** hook próprio (`hooks/usarRelogioDoReplay.ts`) e conta de desenho (`calculosDeTela/geometriaDoRadar.ts`) ficam em `.ts` fora dos componentes. É posição, tempo e tamanho na tela, nunca regra de negócio.
- **Comportamento repetido tem um lugar só:** janela modal com `usarJanelaModal` (abre com `showModal`, fecha no Esc, no botão e no clique fora), movimento reduzido com `prefereMenosMovimento()` (`calculosDeTela/movimento.ts`), rolagem abaixo do cabeçalho fixo com `rolarAteOElemento` (`calculosDeTela/rolagem.ts`) e espera pelo próximo quadro com `depoisDeDesenhar` (`calculosDeTela/desenho.ts`). Não reescreva isso dentro do componente.
- **Formatação de apresentação** (nota com vírgula, data, plural) em `formatacao/formato.ts`, com `Intl` em pt-BR. Formatar não é calcular: nada de regra de negócio ali.
- **Tipos do JSON num único `relatorio/tiposDoRelatorio.ts`**, espelhando os modelos do Python. Mudou o JSON, muda o `tiposDoRelatorio.ts` no mesmo commit.
- **Tokens em português** (`--cor-destaque`, `--fonte-mono`, `--raio`) em `estilos/tokens.css`. O tema segue o sistema; `data-tema="claro"` ou `"escuro"` no `<html>` força um deles.
- Mesmas regras de legibilidade do Python: nomes em português, funções curtas, sem comentários.

## Pastas

Tudo em `frontend/src/`. Cada `.tsx` fica com o seu `.css` ao lado.

- `main.tsx`, `App.tsx`, `App.css`: ponto de entrada e a troca de abas; o `App` guarda o estado da página (tela, foco, tema, janelas abertas) e escolhe a tela.
- `telas/`: a tela "Painel" (`TelaDoPainel`: cabeçalho da análise e zonas) e os tipos que o `App` passa entre as telas (`tiposDaTela.ts`).
- `estilos/`: CSS global da página (tokens, base e fontes embutidas).
- `assets/`: logos e arquivos de fonte usados pelo CSS e pelo favicon.
- `relatorio/`: leitura do JSON embutido no HTML e os tipos que espelham esse JSON.
- `conteudo/`: textos fixos da tela (glossário, zonas, passos do tour e do guia, descrições do pentest).
- `moldura/`: o que envolve as zonas (barras do topo, aviso sem IA, cabeçalho da análise e a caixa de cada zona).
- `zonas/rastreado/`, `zonas/agir/`, `zonas/detalhes/`: os componentes de cada zona do painel, um por pasta.
- `segurancaAtiva/`: a aba "Pentest".
- `janelas/`: o que abre por cima da tela (painel da origem do dado e tour guiado).
- `guia/`: a tela "Como usar".
- `basicos/`: peças pequenas usadas em várias telas (ícone, selos, termo com dica, texto com marcas).
- `hooks/`: hooks próprios (`usar…`): tempo e tamanho na tela, tema, modo foco e janela modal.
- `calculosDeTela/`: contas de posição e desenho, rolagem, movimento reduzido e os `id`s dos elementos, sem JSX.
- `formatacao/`: formatação de números, datas e plurais para exibir.

## Organização da tela

1. **Indicadores:** risco do site, bibliotecas vulneráveis, encontradas só pela IA, primeira ação.
2. **Rastreado:** replay da visita, gravidade × chance de exploração, plano de correção, onde a IA entrou.
3. **Agir:** "O que fazer agora", com cada ação, o porquê, o impacto, quem resolve, "Como verificar" e "Abrir task".
4. **Detalhes:** bibliotecas e checagens.

Clique em qualquer dado abre a origem dele num painel lateral (`PainelOrigemDoDado`, um `<dialog>` modal nativo aberto pelo `usarJanelaModal`: Esc, foco preso e devolvido sem código próprio). O painel só mostra o que o JSON traz: a conta da nota é `nota.conta`, nunca refeita no frontend.

- **Modo foco:** botão "Focar" em cada zona (Rastreado, Agir, Detalhes). O layout completo é o padrão; o foco é só um estado no hook `usarModoFoco` (`zonaEmFoco`, com `entrarNoFoco` e `sairDoFoco`, que volta a rolar até a zona), usado pelo `App`, com `BarraDeFoco` no topo e Esc para sair. A `TelaDoPainel` embrulha cada zona numa `Zona` (nome e "Focar"); as zonas ficam em `conteudo/zonas.ts`. Nenhum componente de zona sabe que está em foco.
- **Tour guiado e Como usar:** a `BarraSuperior` troca entre "Painel", "Pentest" quando há resultado e "Como usar" (estado `tela` no `App`) e abre o `TourGuiado`. Os passos do tour ficam em `conteudo/tour.ts`, cada um com o seletor de uma classe que já existe na tela: o tour só mostra os passos cujo elemento existe, então mudar a classe de um bloco pede a mesma mudança ali. O passo do Pentest só aparece quando a aba foi gerada. Os passos do guia ficam em `conteudo/guia.ts`, com os comandos do README, incluindo a execução opcional do pentest autorizado.
- **Análise sem IA:** `AvisoSemIA` no topo, sempre visível, quando o JSON traz `limitacoes`. Fica presa junto da `BarraSuperior` num único bloco fixo (`app__topo`, no `App.css`), para as duas não se sobreporem. Quem rola a página desconta a altura desse bloco, que o `App` mede e passa por props: nenhum componente procura `.app__topo` por conta própria. O indicador "encontradas só pela IA" mostra "não procurado", nunca zero.
- **Pentest opcional:** `BarraSuperior` mostra a aba "Pentest" só quando o JSON traz `pentest`; `PainelPentest` e `ItemDoPentest` exibem o resultado ativo separado das zonas, da nota e do plano. O JSON só chega ao frontend depois de ser produzido pelo comando `pentest --autorizo`.
- **A confirmar:** bibliotecas barradas pelas travas aparecem numa lista separada (`ListaAConfirmar`), com a trava que falhou, o motivo e como conferir à mão. O "como conferir" é texto fixo por nome de trava, em `zonas/detalhes/ItemAConfirmar.tsx`: trava nova que manda para "a confirmar" ganha a sua linha ali.
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
- Animação só para orientar: entrada dos blocos, reordenação, abertura de painéis. Há duas exceções. O replay da visita (`ReplayDaVisita`) é a única animação contínua do painel: para no fim, tem pausa e com `prefers-reduced-motion` já abre parada no fim. As ilustrações do guia "Como usar" (`IlustracaoDoGuia`) repetem, para mostrar o gesto de cada passo, e ficam paradas com `prefers-reduced-motion`.
