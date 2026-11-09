# Decisão 05: relatório em React num único HTML, com o JSON embutido

Requisitos: R13 e R20.2. Código: `frontend/`, `rastro/relatorio/html.py` e `rastro/relatorio/modelo.html`.

## Contexto

O relatório é lido pelo auditor, pelo dev e pelo PO, e por isso precisa ser interativo: origem de cada dado, glossário, task para copiar, modo foco, tema claro e escuro. Ao mesmo tempo, ele precisa:

- abrir com duplo clique, sem servidor e sem internet (R13.5);
- ir por e-mail ou anexo numa task como um arquivo só;
- exigir só Python de quem usa (R20.2).

## Decisão

- **React + TypeScript**, com o Vite padrão e o `vite-plugin-singlefile`, sem outras bibliotecas. O build gera um `index.html` com JavaScript, CSS, fontes IBM Plex e logo embutidos.
- **O build é versionado** como `rastro/relatorio/modelo.html` (cerca de 470 KB). Quem usa não precisa de Node: só quem mexe no frontend.
- **O Python embute o JSON** da análise no modelo, dentro de `<script id="dados" type="application/json">`, trocando todo `<` por `<`. Assim nenhum `</script>` dos dados fecha a tag antes da hora.
- **O React só mostra.** Toda contagem e todo texto vêm prontos no JSON, e a tela não recalcula nada (R13.7). As regras ficam no Python, onde estão os testes.
- O `relatorio.json` é gravado ao lado do HTML, para quem quiser ler ou integrar os dados.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| HTML montado no Python com texto e `string.Template` | A interatividade viraria JavaScript solto, escrito à mão e sem tipos, difícil de manter e de testar. |
| Jinja2 ou outro motor de modelos | Dependência de produção, e o problema do JavaScript solto continua. |
| Servidor local (Flask, `http.server`) | Exige deixar um processo rodando com uma porta aberta, e o relatório deixa de ser um arquivo que se encaminha. |
| HTML que lê o `relatorio.json` ao lado | Aberto com duplo clique (`file://`), o navegador bloqueia a leitura do arquivo vizinho. |
| React e fontes por CDN | Faria requisição externa: não abre sem internet e avisa terceiros de que o relatório foi aberto (R13.5). |
| Só JSON e terminal | O dev e o PO não leem JSON, e a origem do dado e o glossário se perdem. |
| Outro framework (Vue, Svelte) | Resolveria o mesmo problema. O steering já fixou React + TypeScript, e trocar não traria ganho. |
