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
- **Eventos sobem por props** (`aoClicarFalha(id)`). Só `App.tsx` liga os componentes.
- **Estado só com o React:** `useState` e `useReducer`. O tema escolhido fica no `App` e desce por props; contexto só quando mais de um componente precisar dele.
- **Formatação de apresentação** (nota com vírgula, data, plural) em `componentes/formato.ts`, com `Intl` em pt-BR. Formatar não é calcular: nada de regra de negócio ali.
- **Tipos do JSON num único `tipos.ts`**, espelhando os modelos do Python. Mudou o JSON, muda o `tipos.ts` no mesmo commit.
- **Tokens em português** (`--cor-destaque`, `--fonte-mono`, `--raio`) em `tokens.css`. O tema segue o sistema; `data-tema="claro"` ou `"escuro"` no `<html>` força um deles.
- Mesmas regras de legibilidade do Python: nomes em português, funções curtas, sem comentários.

## Organização da tela

1. **Indicadores:** risco do site, bibliotecas vulneráveis, encontradas só pela IA, primeira ação.
2. **Rastreado:** gravidade × chance de exploração, plano de correção, onde a IA entrou.
3. **Agir:** "O que fazer agora", com cada ação, o porquê, o impacto, quem resolve, "Como verificar" e "Abrir task".
4. **Detalhes:** bibliotecas e checagens.

Clique em qualquer dado abre a origem dele num painel lateral.

- **Modo foco:** botão "Focar" em cada zona (Rastreado, Agir, Detalhes). O layout completo é o padrão; o foco é só um estado no `App.tsx` (`zonaEmFoco`), com `BarraDeFoco` no topo e Esc para sair. Nenhum componente de zona sabe que está em foco.
- **Análise sem IA:** `AvisoSemIA` no topo, sempre visível, quando o JSON traz `limitacoes`. O indicador "encontradas só pela IA" mostra "não procurado", nunca zero.
- **A confirmar:** bibliotecas barradas pelas travas aparecem numa lista separada, com a trava que falhou e como conferir à mão.

## Identidade visual

- **Cores só por tokens** em `tokens.css`, com tema claro e escuro. Nenhuma cor literal em componente.
- Paleta petróleo (`#0F5F7A` claro / `#5BB9D4` escuro); violeta só para IA; vermelho, laranja e verde só para estado.
- Cantos retos: 3 a 4px.
- Fontes: IBM Plex Sans (texto), IBM Plex Sans Condensed (títulos e números), IBM Plex Mono (código e dados). O relatório abre offline: as fontes vão embutidas em woff2 (`src/fontes.css` e `src/assets/fontes/`, subconjunto latin, só os pesos usados, licença OFL ao lado); nada de Google Fonts no build. Peso novo só se a tela usar: um arquivo e um `@font-face` a mais.
- Ícones em traço. Logo: quadrado com dois pontos de rastro até um X.
- Favicon é o logo (`frontend/src/assets/logo-claro.svg` e `logo-escuro.svg`, copiados da identidade visual), embutido no HTML do build pelo `vite.config.ts` (o Vite não embute `<link rel="icon">` sozinho).

## UX e acessibilidade

- Quem usa não é especialista: termos técnicos com explicação ao passar o mouse ou tocar.
- Estado nunca só por cor: sempre com ícone e texto.
- Foco visível, navegação por teclado, `prefers-reduced-motion` respeitado.
- Funciona a partir de 400px de largura, sem rolagem lateral.
- Animação só para orientar: entrada dos blocos, reordenação, abertura de painéis.
