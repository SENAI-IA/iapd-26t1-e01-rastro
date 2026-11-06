# Spike: HAR real e bundle do Juice Shop (T03)

Exploração de 06/11/2026 para responder as perguntas da seção 17 do design sobre o HAR, os bundles e a trava 5. Afeta as seções 5, 6 e 8 do design e os critérios R01.1, R03.1, R06.7 e R21.5.

**O HAR foi gravado pelo Playwright, não exportado à mão no Chrome.** A comparação entre o HAR sanitized e o completo do DevTools fica para a T04, que já exporta os HARs das aplicações-alvo. A seção "A conferir no Chrome" lista o que olhar.

## Como foi feito

- **Alvo:** OWASP Juice Shop 20.3.0, imagem `bkimminich/juice-shop@sha256:42843723…` rodando em `127.0.0.1:3000`, com `docker run --rm`. Nada instalado na máquina.
- **HAR:** playwright-core 1.63 (já no cache do `npx`) dirigindo o Google Chrome 157 instalado, com `recordHar` e `content: "embed"`. Só a página inicial, até a rede parar.
- **Gabarito:** o SBOM CycloneDX do próprio build (`frontend/dist/bom/bom.json` dentro do contêiner), com as versões exatas do que entrou no bundle. O `frontend/package.json` só traz faixas (`^22.0.1`).
- **Scripts:** biblioteca padrão do Python, fora do repositório. A IA foi o Claude, com o comando da T02 (`claude -p --output-format json --tools ""`).

## O HAR

| | Resultado |
|---|---|
| Entradas | 46, em um arquivo de 2,9 MB |
| Conteúdo dos scripts | **vem inteiro** em `response.content.text`, em texto puro |
| `encoding: "base64"` | 18 entradas, só imagens e fonte. Nenhum script veio em base64 |
| Entrada sem `text` | 1: o WebSocket do socket.io (status 101, `size: -1`) |
| Chaves além do padrão HAR | `_resourceType`, `_securityDetails`, `_serverPort`. O Chrome também grava chaves com `_`. O Rastro ignora todas |
| Respostas `text/html` | 2: a página (`/`) e o *polling* do socket.io. A primeira é a página, então a regra do site analisado (R01.7) acerta |
| `Set-Cookie` | **nenhum**. O Juice Shop cria os cookies por JavaScript (`language`, aviso de cookies, boas-vindas), então só aparecem no cabeçalho `Cookie` das requisições, sem atributos |

### Scripts da página inicial

| Arquivo | Tamanho | Conteúdo (pelo SBOM) | Assinatura | Versão no código |
|---|---|---|---|---|
| `main.js` | 1.243 KB | app, Font Awesome, QR code, ngx-translate… | não | só `FA "5.15.4"` |
| `chunk-Cv2YgWUq.js` | 368 KB | Angular e Material | não | `ng-version`, `22.2.2` |
| `chunk-1qQQGal7.js` | 149 KB | rxjs, socket.io e outros | não | nenhuma |
| `polyfills.js` | 35 KB | zone.js | não | nenhuma |
| `scripts.js` | 21 KB | cookieconsent 3.1.1 | não | nenhuma |
| `chunk-DBPdFzgj.js` · `rolldown-runtime-….js` | 2 KB · 0,3 KB | carregador | não | nenhuma |

- Nenhuma assinatura da seção 6 reconheceu algo. É o esperado: não há jQuery, Bootstrap e afins, e os nomes dos arquivos têm só *hash*.
- **O build tira os comentários de licença.** Sobraram dois `/*!*/` vazios. As licenças foram para `3rdpartylicenses.txt`, que o navegador não baixa e por isso não está no HAR.
- Outros 8 chunks (about, web3, carteira, confete…) só entram no HAR se a pessoa visitar a página que os usa. **O HAR mostra só o que foi navegado.**

## Bundles e trechos (R03.1)

Foram três seleções de trechos testadas com a IA, sempre com no máximo 5 trechos por bundle e janelas de 300 caracteres:

| Seleção | Trechos | O que a IA respondeu |
|---|---|---|
| A. Regra do design: `/*!`, `version`, `VERSION` e `\d+\.\d+\.\d+` | 10 | nada: os trechos eram todos coordenadas de SVG (`2.751 13.014 10.044…`) |
| B. Versão entre aspas: `["'`]v?\d+\.\d+\.\d+(-…)?["'`]` | 2 | `@angular/core@22.2.2` em 3 de 3 tentativas, certo pelo SBOM |
| C. Início de scripts sem versão (cookieconsent, zone.js, rxjs) | 3 | nada. **A IA não inventou versão** |

- O número solto `\d+\.\d+\.\d+` e a palavra `version` só trazem ruído: caminhos SVG e propriedades como `version:0` e `this.version=40`. **Vale só a versão entre aspas**, que o minificador mantém como string.
- O comentário de licença continua na regra, mas só quando tem conteúdo (`/*!*/` vazio é ignorado). Ele importa nos sites antigos, sem build moderno.
- **Corte de 30 KB:** os dois bundles que tinham versão têm mais de 140 KB. O único script abaixo do corte com biblioteca (`scripts.js`, cookieconsent) não tem versão no código. O corte fica.
- Com a seleção B, a IA recebeu 2 trechos para 1,8 MB de JavaScript. Cerca de 27 mil tokens de entrada, quase tudo prompt de sistema da CLI (ver T02), e entre US$ 0,02 e 0,06 por chamada.

### O que a IA acertou e errou

| Trecho | Respostas | Certo pelo SBOM |
|---|---|---|
| `[`ng-version`,`22.2.2`]` | `@angular/core@22.2.2` (3 de 3) | sim |
| `U$1=`FA "5.15.4"`` | nada (3 de 5) ou `@fortawesome/fontawesome-free@5.15.4` (2 de 5) | **não**: no bundle estão `fontawesome-svg-core@1.2.36` e `free-*-svg-icons@5.15.4`. O `fontawesome-free` não está |

O caso do Font Awesome é o de que a trava 5 precisa cuidar. O pacote existe e a versão existe e está no trecho, então as travas 1 a 4 deixam passar.

### Alcance no Juice Shop

- **Dos 103 pacotes do SBOM, a IA só pode provar um:** o `@angular/core`. As outras não deixam versão no bundle de produção.
- **Nenhuma biblioteca de front-end do Juice Shop 20.3.0 tem aviso** no GitHub Advisory: o Angular 22.2.2, o lodash-es 4.18.1, o socket.io-client 4.8.4, o cookieconsent 3.1.1 e o fontawesome-free 5.15.4 voltaram sem nenhum. As falhas do Juice Shop estão no servidor, que o Rastro não vê.
- Para a T04: o Juice Shop serve para mostrar a identificação por IA (o aceite da T41 continua possível), mas **não conta como alvo com biblioteca vulnerável**. A avaliação precisa de pelo menos dois sites com bibliotecas antigas, de preferência servidas com nome de arquivo ou comentário de licença.

## A trava 5 (R21.5)

O `.tgz` de cada pacote foi lido em memória, com a integridade conferida (`sha512` contra `dist.integrity`). Foram lidos os `.js`, os `.mjs` e os `.cjs`: o Angular só publica `.mjs`.

| Pacote | `.tgz` | Desempacotado | Tempo |
|---|---|---|---|
| `@angular/core@22.2.2` | 1,6 MB | 7,1 MB | 0,5 s |
| `@angular/common@22.2.2` | 0,9 MB | 9,3 MB | 0,6 s |
| `@fortawesome/fontawesome-free@5.15.4` | 4,3 MB | 11,8 MB | 0,7 s |
| `@fortawesome/fontawesome-svg-core@1.2.36` | 0,04 MB | 0,2 MB | 0,1 s |
| `lodash-es@4.18.1` | 0,15 MB | 0,6 MB | 0,2 s |

O limite de 10 MB vale para o `.tgz` baixado, e todos ficaram bem abaixo dele.

### Critérios comparados

- **C1:** o trecho, sem espaços, aparece em algum arquivo do pacote (a proposta do design).
- **C2:** a versão do trecho aparece no pacote (a alternativa do design).
- **C3:** as strings do trecho aparecem como strings no pacote, comparando o texto escrito.
- **C4:** como o C3, mas comparando **o valor** da string (sem as aspas e com os escapes resolvidos). Além disso, o trecho precisa ter a versão e pelo menos uma string a mais, com 3 caracteres ou mais além da versão.

| Caso | Pacote | Esperado | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|
| Acerto da IA | `@angular/core@22.2.2` | passa | barra | passa | passa | **passa** |
| Versão vizinha, trecho real | `@angular/core@22.2.1` | barra | barra | barra | barra | **barra** |
| Versão antiga, trecho real | `@angular/core@21.0.0` | barra | barra | barra | barra | **barra** |
| Pacote irmão, mesma versão | `@angular/common@22.2.2` | barra | barra | passa | barra | **barra** |
| Pacote sem relação | `lodash-es@4.18.1` | barra | barra | barra | barra | **barra** |
| Trecho inventado `[`ng-versao`,`22.2.2`]` | `@angular/core@22.2.2` | barra | barra | passa | barra | **barra** |
| Só a versão `` `22.2.2` `` | `@angular/core@22.2.2` | barra | barra | passa | passa | **barra** |
| Erro da IA: Font Awesome | `@fortawesome/fontawesome-free@5.15.4` | barra | barra | passa | barra | barra* |

- **C1 nunca passa:** o minificador renomeia as variáveis (`uI`, `WC`) e troca o formato do código. Está descartado.
- **C2 deixa passar invenção:** basta a versão existir no pacote. Está descartado.
- **C3 erra a forma das aspas:** no pacote está `"FA \"5.15.4\""` e no bundle, `` `FA "5.15.4"` ``. Também aceita "só a versão".
- **C4 acerta todos os casos.** É o critério que vai para o design.

\* **Limite do C4:** o `fontawesome-free` traz por dentro o mesmo código do `svg-core`, inclusive `FA "5.15.4"`. Ele só foi barrado porque "FA" tem menos de 3 caracteres. Um pacote que redistribui o código de outro na mesma versão passa pela trava 5, que confere só se o código é daquele pacote. Por isso a biblioteca da IA aparece sempre com o método "ia" e o trecho como evidência (R03.2).

## O que fica para o código (T08, T40 e T41)

- **T08:** script em texto puro é o caso comum, e base64 continua tratado (R01.4). Ignorar chaves com `_` e entrada sem `text`.
- **T41:**
  - extrair só comentários `/*!` com conteúdo e janelas de 300 caracteres em volta de versões entre aspas, no máximo 5 por bundle;
  - manter o corte de 30 KB;
  - no prompt, pedir "só com a versão no trecho; se nada provar, lista vazia". Com isso, a IA não inventou nada em scripts sem versão.
- **T40:**
  - ler `.js`, `.mjs` e `.cjs`;
  - comparar o valor das strings, não o texto (C4);
  - para os testes, montar `.tgz` com o caso do Angular (passa) e os casos de versão vizinha, pacote irmão, trecho inventado e "só a versão" (barram).

## A conferir no Chrome (na T04)

Exportar do DevTools, na mesma navegação, o HAR **sanitized** e o **completo** (*with sensitive data*) e conferir:

- Se o conteúdo dos scripts vem em `text` nos dois, e se algum vem em base64.
- O que o sanitized remove além de `Cookie`, `Set-Cookie` e `Authorization`: se esvazia `request.cookies`/`response.cookies`, se mexe em query string, corpo ou outros cabeçalhos.
- Se a regra de R06.7 ("HAR sem cookies") separa os dois casos que este spike mostrou: HAR sanitized, e site que cria cookies só por JavaScript, que também chega sem `Set-Cookie` mesmo no HAR completo. No segundo caso, sugerir "exporte o HAR completo" não ajuda.

## O que foi ajustado na spec

- `design.md`, seção 5: o conteúdo dos scripts vem em `text`, chaves com `_` ignoradas.
- `design.md`, seção 6: corte de 30 KB confirmado e seleção de trechos trocada (versão entre aspas, licença com conteúdo), sem `[spike]`.
- `design.md`, seção 8: `.mjs` e `.cjs` na leitura do pacote e o critério C4 da trava 5, com o limite do pacote que redistribui código, sem `[spike]`.
- `design.md`, seção 17: as perguntas de bundles e da trava 5 respondidas; a do HAR sanitized passa para a T04.
- `requirements.md`: R03.1 e R21.5 sem `[spike]`. R02.4 continua com `[spike]`: a lista sai dos alvos da T04.
- `tasks.md`: a T04 passa a conferir o HAR sanitized e o completo no Chrome e a ter dois alvos além do Juice Shop.
