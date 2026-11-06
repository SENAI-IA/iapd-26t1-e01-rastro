# Avaliação do Rastro (T04)

HARs de aplicações reais e o gabarito com as bibliotecas e versões que cada uma serve de verdade. É com eles que se medem as métricas do PRD: o que o Rastro acha com e sem IA, e se alguma biblioteca é confirmada fora do gabarito.

## Alvos

| Alvo | O que mostra | Bibliotecas com aviso |
|---|---|---|
| **OWASP WebGoat 2023.8** | bibliotecas servidas uma a uma, com comentário de licença | 7: jQuery 3.4.1 e 2.1.4, jQuery UI 1.12.1 e 1.10.3, Bootstrap 3.1.1, Underscore 1.10.2, RequireJS 2.3.6 |
| **Drupal 8.6.18** | bundles agregados pelo Drupal, várias bibliotecas num script só | 4: jQuery 3.2.1, jQuery UI 1.12.1, Underscore 1.8.3, CKEditor 4.10.1 |
| **OWASP Juice Shop 20.3.0** | bundle moderno (Angular), sem comentário de licença: o caso da IA | nenhuma (spike T03) |

O detalhe de cada biblioteca (em arquivo ou em bundle, onde a versão aparece, método esperado, avisos) está em `gabarito.json`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `gabarito.json` | bibliotecas, versões e avisos de cada alvo |
| `webgoat.har` | 72 entradas, 39 scripts, 2,1 MB |
| `drupal.har` | 157 entradas, 27 scripts, 4,2 MB |
| `juiceshop.har` | 50 entradas, 7 scripts, 3,0 MB |

**Só HAR sanitized no repositório.** O completo fica fora (o `.gitignore` ignora `*.har`, menos os desta pasta e os de `tests/`).

## De onde vêm as versões

Do próprio alvo, nunca de memória:

- **WebGoat:** os arquivos em `BOOT-INF/classes/webgoat/static/js/libs/` do `webgoat.jar`, pelo comentário de licença e pelo `VERSION` no código.
- **Drupal:** o `core/core.libraries.yml`, conferido com os comentários dos arquivos servidos.
- **Juice Shop:** o SBOM CycloneDX do build (`frontend/dist/bom/bom.json`). O bundle de cada pacote vem do spike T03.
- **Avisos:** `GET https://api.github.com/advisories?ecosystem=npm&affects=<pacote>@<versão>`, em 06/11/2026. O do cookieconsent 3.1.1 é o da T03, do mesmo dia: o limite sem token acabou antes.
- **Publicado no npm:** `GET https://registry.npmjs.org/<pacote>/<versão>`.

## Como gravar de novo

Tudo local, em `127.0.0.1`, com `docker run --rm` (nada instalado na máquina):

```
docker run --rm -d --name rastro-webgoat -p 127.0.0.1:8080:8080 webgoat/webgoat@sha256:01672eb9aeba60d042ae1131d6de683b98fa64e9da60fa5d3daad2642a6795dd
docker run --rm -d --name rastro-drupal -p 127.0.0.1:8888:8888 drupal@sha256:6b33b1f96b13aab3c4280fa8362a6fb32194b2656191b5c9b85f2cb014a8d942 php -d memory_limit=512M core/scripts/drupal quick-start standard --host 0.0.0.0 --port 8888 --suppress-login
docker run --rm -d --name rastro-juice -p 127.0.0.1:3000:3000 bkimminich/juice-shop@sha256:42843723a7bf4246aa5d63c324978b17ef296ac78434aeddd34c427bfb5853f4
```

- **Navegador:** playwright-core 1.63 (do cache do `npx`) dirigindo o Google Chrome 157 instalado, com `recordHar: { content: "embed" }`.
- **Login fora da gravação:** o cadastro e o login (WebGoat) e o link de uso único do `quick-start` (Drupal, em `docker logs rastro-drupal`) rodam num contexto sem HAR. Só a navegação, já com a sessão, é gravada. No Drupal, o preparo também cria um artigo, para existir `/node/1`.
- **Páginas:** as de `paginas` no gabarito, cada uma até a rede parar.
- **Sanitização:** tira os cabeçalhos `Cookie`, `Set-Cookie`, `Authorization` e `Proxy-Authorization` e esvazia `request.cookies` e `response.cookies`. Ficam os tokens CSRF do Drupal na URL (`?token=`), de um contêiner que já não existe. O sanitized do Chrome também mantém a URL.

## O que a avaliação mostrou

Um protótipo das assinaturas, rodado nos três HARs (fora do repositório), acha as 11 bibliotecas com aviso e nenhuma fora do gabarito, desde que a seção 6 do design siga os quatro ajustes abaixo, já feitos:

1. **Bundle agregado:** o Drupal junta jQuery, Underscore, jQuery UI, jQuery Form, jquery.cookie e jQuery Once num script só, e cada um mantém o próprio comentário. O comentário passa a ser procurado no conteúdo inteiro, não só nos primeiros 2 KB.
2. **Comentário dentro de comentário:** o jQuery Form diz `Requires jQuery v1.7.2 or later`. O padrão começa no início do comentário, para não registrar jQuery 1.7.2.
3. **Nome × conteúdo:** o WebGoat serve `jquery-ui-1.10.4.js` com a jQuery UI 1.10.3 dentro. Vale o comentário.
4. **Versão na URL:** o Drupal serve `ckeditor.js?v=4.10.1`. O `?v=` e o `?ver=` contam como nome do arquivo.

E três pontos que ainda não mudaram a spec:

- **A decidir: trava 4 nas assinaturas.** A jQuery UI 1.10.3 (6 avisos, um alto) não foi publicada no npm, que só tem a jQuery UI a partir da 1.10.4. Pela R21.4, a trava 4 vale também para a assinatura, e a biblioteca iria para "a confirmar", fora da nota e do plano. O GitHub Advisory responde normalmente para essa versão.
- **Pacote renomeado:** a 4.10.1 do CKEditor só existe no npm como `ckeditor`, que tem 1 aviso. Os avisos posteriores a 2020 estão em `ckeditor4`, que começa na 4.13.0. Pela faixa, 13 deles também valem para a 4.10.1, mas a consulta por `ckeditor` não os traz.
- **Fora do alcance:** a versão do Backbone só aparece no código (`VERSION="1.2.3"`), e jQuery Form, jquery.cookie, jQuery Once e Modernizr não estão na lista de assinaturas. Nenhum deles tem aviso. Os avisos do próprio Drupal (pacote `drupal/core` do Composer) não são de front-end npm.

Na IA: no Juice Shop, a única prova possível é o `@angular/core` (spike T03). No WebGoat, o `jquery.form.js` (42 KB, sem assinatura) vai para a IA, mas a 3.51.0 não foi publicada no npm e a trava 4 a barra. O bundle de 78 KB do Drupal sem assinatura (matchMedia, Joyride) não tem versão no código: a resposta certa é lista vazia.

## Pendente: exportação manual no Chrome

Os HARs daqui foram gravados pelo Playwright. Falta exportar à mão, do DevTools do Chrome, numa mesma navegação de um dos alvos com sessão (Drupal logado, por exemplo), o HAR **sanitized** e o **completo** (*with sensitive data*), e conferir a lista "A conferir no Chrome" de `docs/spike/har-e-bundles.md`:

- se o conteúdo dos scripts vem em `text` nos dois, e se algum vem em base64;
- o que o sanitized remove além de `Cookie`, `Set-Cookie` e `Authorization` (`cookies[]`, query string, corpo, outros cabeçalhos);
- se a regra de R06.7 separa o HAR sanitized do site que cria cookies só por JavaScript (Juice Shop).

O resultado entra neste README e na seção 17 do design. Se o sanitized do Chrome remover mais do que a sanitização daqui, os HARs desta pasta são gerados de novo com a mesma regra.
