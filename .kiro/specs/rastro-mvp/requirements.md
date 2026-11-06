# Requisitos: Rastro MVP

**O quê e por quê.** Este arquivo diz o que o MVP faz, sem dizer como. Ele parte do PRD (`docs/prd.pdf`, RF01 a RF16) e do que ele define como escopo do MVP.

## Como ler

Cada requisito tem uma história e critérios de aceite em **EARS** (Easy Approach to Requirements Syntax), escritos em português:

| Padrão | Quando usar | Forma |
|---|---|---|
| Sempre | regra que vale o tempo todo | O Rastro DEVE … |
| Evento | resposta a uma ação ou entrada | QUANDO <gatilho>, o Rastro DEVE … |
| Indesejado | erro ou caso ruim | SE <condição>, ENTÃO o Rastro DEVE … |
| Estado | enquanto algo vale | ENQUANTO <estado>, o Rastro DEVE … |
| Opcional | só quando uma opção é usada | ONDE <opção>, o Rastro DEVE … |

**Cada critério tem um ID (`R05.2`) e vira um teste.** O teste leva o ID no nome, por exemplo `test_r05_2_prioridade_alta_a_partir_de_7_5`. Os critérios que só dá para conferir olhando a tela estão marcados como *(verificação manual)*.

Marcados com **[spike]**: os critérios que dependem do que o spike mostrar. Eles podem mudar antes de virar código.

## Termos

| Termo | Significado aqui |
|---|---|
| HAR | Arquivo JSON com a navegação gravada no DevTools do navegador. |
| Requisição | Uma entrada do HAR: pedido e resposta. |
| Biblioteca | Pacote front-end identificado, com nome npm e versão. |
| Bundle | Arquivo JavaScript que junta várias bibliotecas e esconde nome e versão. |
| Aviso | Falha publicada no GitHub Advisory (GHSA), com CVE quando houver. |
| Achado | Um aviso que atinge uma biblioteca encontrada no HAR. |
| Checagem | Regra sobre cabeçalhos ou cookies do site. |
| Nota de risco | Número de 0 a 10 calculado pela fórmula fixa. |
| Provedor de IA | A CLI usada para falar com a IA: Kiro, Claude ou Codex. |

---

## R01 Ler o HAR (RF01)

**Como** auditor, **quero** passar o HAR exportado do navegador **para** analisar o site sem mexer nele.

1. QUANDO o auditor executar `python -m rastro analisar <arquivo.har>`, o Rastro DEVE ler o arquivo em UTF-8 e extrair as requisições, com URL, método, status, cabeçalhos, cookies e conteúdo da resposta.
2. SE o arquivo não existir, ENTÃO o Rastro DEVE encerrar com código 1 e uma mensagem com o caminho informado.
3. SE o conteúdo não for JSON ou não tiver `log.entries`, ENTÃO o Rastro DEVE encerrar com código 1, a mensagem "o arquivo não é um HAR válido" e nenhum relatório.
4. QUANDO o conteúdo de uma resposta vier em base64, o Rastro DEVE decodificá-lo antes de analisar.
5. O Rastro DEVE abrir o HAR só para leitura e nunca alterá-lo.
6. SE nenhuma resposta do HAR trouxer conteúdo JavaScript, ENTÃO o Rastro DEVE seguir com as checagens e avisar no relatório que nenhuma biblioteca pôde ser analisada e por quê.
7. O Rastro DEVE considerar como **site analisado** o host da primeira resposta HTML do HAR.

## R02 Identificar bibliotecas por assinatura (RF02)

**Como** auditor, **quero** que o Rastro reconheça as bibliotecas pelo nome do arquivo ou pelo comentário de versão **para** não depender de IA no caso simples.

1. QUANDO a URL de um script trouxer nome e versão de uma biblioteca conhecida (ex.: `jquery-3.4.1.min.js`, `/lodash@4.17.15/`), o Rastro DEVE registrar a biblioteca com método "assinatura" e a URL como evidência.
2. QUANDO o conteúdo de um script trouxer um comentário de versão conhecido (ex.: `/*! jQuery v3.4.1`), o Rastro DEVE registrar a biblioteca com método "assinatura" e o trecho do comentário como evidência.
3. QUANDO a mesma biblioteca e versão aparecerem em mais de uma requisição, o Rastro DEVE registrá-la uma vez só, guardando todas as requisições como evidência.
4. O Rastro DEVE reconhecer por assinatura, no mínimo, jQuery, jQuery UI, Bootstrap, Lodash, Moment.js e AngularJS. **[spike]** A lista final sai das aplicações da avaliação.
5. O Rastro DEVE registrar cada biblioteca com nome do pacote npm, versão, método de identificação e evidência.

## R03 Identificar bibliotecas em bundles com IA (RF03)

**Como** auditor, **quero** que a IA reconheça bibliotecas escondidas em bundles **para** não perder falhas que a assinatura não vê.

1. QUANDO um script não for reconhecido por assinatura e tiver tamanho de bundle, o Rastro DEVE enviar à IA trechos selecionados do código e pedir nome, versão e o trecho que prova a resposta. **[spike]** O tamanho mínimo e a seleção de trechos saem do teste no Juice Shop.
2. O Rastro DEVE registrar cada biblioteca reconhecida pela IA com método "ia" e o trecho usado como evidência.
3. O Rastro DEVE passar cada biblioteca devolvida pela IA pelas travas de R21 antes de usá-la. Quem confirma é a trava, nunca a IA.
4. SE a biblioteca não passar em todas as travas, ENTÃO o Rastro DEVE mostrá-la na lista "a confirmar", com a trava que falhou e como confirmar à mão, fora da nota, do resumo e do plano de ação.
5. SE a resposta da IA vier fora do formato esperado ou a chamada falhar, ENTÃO o Rastro DEVE seguir a análise sem essas bibliotecas e registrar a falha no painel da IA.

## R04 Consultar o GitHub Advisory (RF04)

**Como** auditor, **quero** saber quais falhas conhecidas atingem cada biblioteca **para** não pesquisar uma por uma.

1. QUANDO houver biblioteca identificada, o Rastro DEVE consultar o GitHub Advisory pelo ecossistema npm e por `pacote@versão`.
2. O Rastro DEVE registrar, para cada aviso: ID GHSA, CVE (quando houver), resumo, CVSS, percentil EPSS, faixa de versões afetadas, primeira versão corrigida e link do aviso.
3. SE a consulta de uma biblioteca falhar (sem rede, limite de requisições, erro do servidor), ENTÃO o Rastro DEVE seguir com as demais e marcar essa biblioteca como "não consultada", com o motivo.
4. ONDE a variável `GITHUB_TOKEN` estiver definida, o Rastro DEVE usá-la na consulta. **[spike]** Confirmar se o limite sem token basta.
5. O Rastro DEVE consultar só fontes oficiais de vulnerabilidades: o GitHub Advisory e, se a extensão R04A for entregue, o OSV e o NVD. O registro do npm (R21) serve só para conferir pacotes, não para buscar falhas.

### R04A Extensão opcional: OSV e NVD (só se houver tempo)

O GitHub Advisory é a fonte do MVP. OSV e NVD entram **só se** as fases 1 e 2 fecharem no prazo; senão, vão para os planos futuros sem mudar nada do resto. Cada fonte é um conector a mais, atrás da mesma interface.

1. QUANDO houver biblioteca identificada, o Rastro DEVE consultar também o OSV por pacote npm e versão.
2. QUANDO um aviso tiver CVE e vier sem CVSS, o Rastro DEVE buscar o CVSS desse CVE no NVD.
3. O Rastro DEVE juntar avisos iguais de fontes diferentes pelo ID e pelos apelidos (GHSA, CVE, ID do OSV) e mostrar um aviso só, com todas as fontes que o citam.
4. QUANDO as fontes discordarem, o Rastro DEVE seguir uma ordem fixa: GitHub Advisory, depois OSV, depois NVD, para resumo, faixa e versão corrigida; para o CVSS, GitHub e depois NVD. O EPSS vem só do GitHub.
5. O Rastro DEVE mostrar, na origem de cada aviso, de qual fonte veio cada campo.
6. SE o OSV ou o NVD falharem, ENTÃO o Rastro DEVE seguir só com o GitHub e registrar no relatório qual fonte não respondeu.
7. ONDE a variável `NVD_API_KEY` estiver definida, o Rastro DEVE usá-la na consulta ao NVD.

## R05 Calcular a nota de risco e a prioridade (RF05)

**Como** auditor, **quero** uma nota única e explicável por achado **para** saber o que corrigir primeiro.

1. O Rastro DEVE calcular a nota como `10 × (0,5 × CVSS/10 + 0,5 × percentil EPSS)`, arredondada a uma casa decimal.
2. O Rastro DEVE classificar a prioridade como alta (nota ≥ 7,5), média (nota ≥ 6,5) ou baixa (abaixo de 6,5).
3. SE o aviso não tiver EPSS, ENTÃO o Rastro DEVE usar a nota igual ao CVSS e mostrar o selo "sem EPSS". **[spike]** Validar com a frequência real de EPSS vazio.
4. SE o aviso não tiver CVSS, ENTÃO o Rastro DEVE mostrá-lo com "sem nota" e prioridade "a avaliar", sem escondê-lo.
5. O Rastro DEVE usar como nota da biblioteca a maior nota entre os seus achados.
6. O Rastro DEVE ordenar os achados por nota decrescente e, no empate, por CVSS decrescente.
7. A nota e a prioridade DEVEM vir só da fórmula. A IA não altera nota, prioridade nem ordem.

## R06 Checar cabeçalhos e cookies (RF06)

**Como** auditor, **quero** saber se o site deixa de usar proteções básicas do navegador **para** corrigir o que é barato de corrigir.

1. QUANDO uma resposta HTML do site analisado não tiver `Content-Security-Policy`, o Rastro DEVE registrar a checagem "CSP ausente".
2. QUANDO o site analisado usar HTTPS e não enviar `Strict-Transport-Security`, o Rastro DEVE registrar "HSTS ausente".
3. QUANDO uma resposta HTML do site analisado não tiver `X-Content-Type-Options: nosniff`, o Rastro DEVE registrar "nosniff ausente".
4. QUANDO uma resposta HTML do site analisado não tiver `X-Frame-Options` nem `frame-ancestors` na CSP, o Rastro DEVE registrar "proteção contra frame ausente".
5. QUANDO os cabeçalhos `Server` ou `X-Powered-By` trouxerem número de versão, o Rastro DEVE registrar "servidor expõe versão".
6. QUANDO um cookie do site analisado não tiver `HttpOnly`, `Secure` (em HTTPS) ou `SameSite`, o Rastro DEVE registrar uma checagem para cada atributo ausente, com o nome do cookie e nunca o valor.
7. SE o HAR não trouxer cookies (ex.: exportado no modo sanitized), ENTÃO o Rastro DEVE marcar as checagens de cookie como "não verificadas", e não como aprovadas, e dizer no relatório que exportar o HAR completo inclui essas três checagens.
8. O Rastro DEVE registrar em cada checagem a severidade fixa da regra, quem resolve e a requisição usada como evidência.

## R07 Explicar cada achado com IA (RF07)

**Como** auditor que não é especialista, **quero** entender cada achado em linguagem simples **para** decidir e explicar ao time.

1. QUANDO uma biblioteca tiver achados, o Rastro DEVE pedir à IA uma explicação em linguagem simples (o que é, o impacto descrito no aviso, como corrigir), sem afirmar nada sobre o site que não esteja na entrada e um teste de verificação.
2. O Rastro DEVE enviar à IA só pacote, versão, avisos (ID, resumo, versões afetadas e corrigidas) e a URL do script sem query string.
3. SE a IA falhar, responder fora do formato ou não passar nas travas de R21.6, ENTÃO o Rastro DEVE mostrar o resumo do próprio aviso e o selo "sem explicação da IA".
4. O Rastro DEVE marcar todo texto gerado pela IA como "gerado por IA" no relatório, e o teste de verificação como "sugerido pela IA: confira antes de usar".

## R08 Montar o plano de ação (RF08)

**Como** auditor, **quero** uma lista do que fazer, em ordem **para** agir sem ter que interpretar tabela.

1. O Rastro DEVE criar uma ação por biblioteca com achados: atualizar `<pacote>` da versão atual para a menor versão que corrige todos os avisos dela.
2. O Rastro DEVE criar uma ação por checagem com falha.
3. Cada ação DEVE trazer o que fazer, o porquê (avisos ou regra e nota), o impacto e quem resolve.
4. SE algum aviso da biblioteca não tiver versão corrigida, ENTÃO a ação DEVE dizer "sem correção publicada: avaliar troca ou mitigação".
5. O Rastro DEVE ordenar as ações por prioridade e, dentro dela, por nota decrescente.

## R09 Gerar o texto da task (RF09)

**Como** auditor, **quero** a task pronta para colar no board **para** não reescrever o achado.

1. O Rastro DEVE gerar, para cada ação, um texto em Markdown com título, contexto, o que fazer, critério de aceite e checklist de evidências (versão antes e depois, teste de verificação, novo HAR sem o achado).
2. QUANDO o auditor clicar em "Abrir task" no relatório, o relatório DEVE mostrar o texto com um botão de copiar. *(verificação manual)*

## R10 Mostrar a origem de cada dado (RF10)

**Como** auditor, **quero** ver de onde veio cada número **para** confiar no relatório e defendê-lo.

1. O Rastro DEVE registrar a origem de cada biblioteca (índice e URL da requisição no HAR, método, evidência), de cada aviso (ID e link) e de cada nota (conta com os valores usados).
2. QUANDO o auditor clicar num dado do relatório, o relatório DEVE abrir um painel lateral com a origem: HAR → identificação → aviso → cálculo. *(verificação manual)*

## R11 Mostrar o que a IA fez (RF11)

**Como** auditor e banca, **quero** ver o que a IA recebeu e devolveu **para** saber quanto ela ajudou e quanto custou.

1. O Rastro DEVE registrar cada chamada à IA com etapa, provedor, entrada enviada, resposta, duração e tokens.
2. SE o provedor não informar tokens, ENTÃO o Rastro DEVE registrar "não informado", nunca uma estimativa.
3. O Rastro DEVE calcular, para o painel "Onde a IA entrou", quantas bibliotecas e achados vieram só por assinatura e quantos vieram com a IA.

## R12 Explicar termos técnicos (RF12)

**Como** auditor que não é especialista, **quero** ver o significado dos termos técnicos na própria tela **para** não sair do relatório para pesquisar.

1. O relatório DEVE sublinhar os termos do glossário e mostrar a definição ao passar o mouse, focar pelo teclado ou tocar. *(verificação manual)*
2. Os termos e definições DEVEM ficar num único arquivo de dados do frontend.

## R13 Gerar o relatório em JSON e HTML (RF13)

**Como** auditor, **quero** um relatório que abre com duplo clique **para** mostrar ao time sem instalar nada.

1. QUANDO a análise terminar, o Rastro DEVE gravar `relatorio.json` e `relatorio.html` numa pasta nova, organizada por aplicação e por data e hora: `<pasta padrão>/<site analisado>/<AAAA-MM-DD_HH-MM-SS>/`.
2. A pasta padrão DEVE ser `Rastro/relatorios` dentro da pasta do usuário, a mesma regra no Windows (`C:\Users\<nome>\Rastro\relatorios`) e no Linux (`~/Rastro/relatorios`). ONDE a opção `--saida <pasta>` for usada, o Rastro DEVE usar essa pasta no lugar da padrão, com a mesma organização dentro dela.
3. SE o HAR não tiver site analisado (R01.7), ENTÃO o Rastro DEVE usar o nome do arquivo HAR no lugar do site. Caracteres que não valem em nome de pasta no Windows (como `:` da porta) viram `_`.
4. SE a pasta da análise já existir, ENTÃO o Rastro DEVE encerrar com código 1 sem gravar nada e dizer qual pasta já existe. O Rastro nunca sobrescreve um relatório.
5. O relatório HTML DEVE abrir offline, com duplo clique, sem fazer nenhuma requisição externa.
6. O relatório HTML DEVE ter tema claro e escuro e ser legível em tela de 400px. *(verificação manual)*
7. O JSON DEVE trazer o campo `versao_formato`, e o HTML DEVE exibir exatamente os dados do JSON, sem recalcular nada.
8. QUANDO a análise terminar, o Rastro DEVE mostrar no terminal o caminho da pasta e do `relatorio.html` e um resumo de uma linha.

## R14 Escolher a IA (RF14)

**Como** auditor, **quero** escolher qual IA usar **para** aproveitar a que já tenho instalada.

1. O Rastro DEVE escolher o provedor por `--ia`; sem a opção, por `RASTRO_IA`; sem os dois, usar o Kiro.
2. SE o provedor informado não for `kiro`, `claude` ou `codex`, ENTÃO o Rastro DEVE encerrar com código 1 listando as opções válidas.
3. SE a CLI do provedor não for encontrada no sistema, ENTÃO o Rastro DEVE encerrar com código 1 antes de ler o HAR, dizendo qual CLI faltou, que `--sem-ia` roda a análise sem IA e o que se perde com isso (ver 5).
4. O Rastro DEVE enviar o prompt pela entrada padrão da CLI, nunca como argumento.
5. ONDE a opção `--sem-ia` for usada, o Rastro NÃO DEVE chamar a IA e DEVE deixar claro, no terminal e no relatório, que a análise está incompleta:
   - bibliotecas escondidas em bundles **não foram procuradas** e podem existir falhas que não aparecem;
   - os achados trazem o resumo do próprio aviso, sem explicação em linguagem simples nem teste de verificação;
   - a nota, a prioridade, as checagens e o plano de ação são os mesmos de uma análise com IA.
6. ONDE a opção `--sem-ia` for usada, o relatório DEVE mostrar esse aviso no topo, sempre visível, e o indicador "encontradas só pela IA" DEVE aparecer como "não procurado", e não como zero.
7. O texto de ajuda (`--help`) DEVE descrever `--sem-ia` com o que se perde, na mesma linha da opção.
8. O relatório DEVE informar qual provedor foi usado.

## R15 Ler uma zona por vez (modo foco) (RF15)

**Como** auditor, dev ou PO, **quero** focar numa zona do relatório **para** ler com clareza, usando a tela toda, sem o resto em volta.

1. O relatório DEVE abrir no layout completo. O modo foco é opcional e nunca é o padrão.
2. O relatório DEVE ter um botão "Focar" em cada zona: Rastreado, Agir e Detalhes.
3. QUANDO o auditor acionar "Focar", a zona DEVE ocupar a largura útil da tela e as outras zonas DEVEM sair de vista. Uma barra fina no topo mostra a zona atual, permite trocar de zona e tem "Sair do foco". *(verificação manual)*
4. QUANDO o auditor apertar Esc ou "Sair do foco", o relatório DEVE voltar ao layout completo, na posição da zona que estava em foco. *(verificação manual)*
5. ENQUANTO uma zona estiver em foco, o painel de origem, o glossário, a task e o aviso de análise sem IA DEVEM continuar funcionando. *(verificação manual)*
6. O modo foco DEVE funcionar por teclado e em tela de 400px. *(verificação manual)*
7. O modo foco DEVE mudar só a apresentação: dados, ordem e textos são os mesmos do layout completo.

---

## Requisitos não funcionais

## R16 Passivo e privado

1. O Rastro NÃO DEVE fazer nenhuma requisição ao site analisado.
2. O Rastro DEVE acessar a rede só para consultar as fontes de R04 e R04A e, em modo leitura, o registro do npm (R21); a IA é acessada pela CLI do provedor.
3. O Rastro NÃO DEVE enviar à IA cookies, cabeçalhos, corpos de requisição, query strings nem trechos que pareçam token (JWT, `Bearer`, chaves longas).
4. O relatório NÃO DEVE conter valores de cookies, de cabeçalhos de autenticação nem tokens do HAR, mesmo quando o HAR for completo. Dos cookies, só o nome e os atributos.
5. O Rastro DEVE aceitar HAR sanitized e HAR completo. O sanitized é o recomendado; o completo só acrescenta as checagens de cookie (C06 a C08).

## R17 Seguro para a máquina

1. O Rastro DEVE gravar só os dois arquivos do relatório, sempre como arquivos novos.
2. O Rastro NÃO DEVE instalar nada global, pedir `sudo` nem apagar arquivos.

## R18 Windows e Linux

1. O Rastro DEVE funcionar em Windows e Linux com os mesmos comandos, exceto a ativação do venv.
2. A verificação (`ruff`, `mypy` e `pytest`) DEVE passar no Windows e no Linux, rodada na máquina local. Não há CI: antes de cada entrega, o resultado nos dois sistemas fica registrado em `docs/cobertura/`.

## R19 Qualidade

1. A cobertura das regras de negócio DEVE ser de pelo menos 60% (meta 80%), medida com `pytest-cov`, com relatório em `docs/cobertura/`.
2. Os testes NÃO DEVEM acessar a rede nem chamar a IA de verdade.
3. O código DEVE passar no `ruff` e no `mypy` sem erros.

## R20 Entrega

1. O repositório DEVE ter um README que outra pessoa consegue seguir para instalar e rodar o Rastro na própria máquina, com comandos para Windows e Linux.
2. Para usar, o Rastro DEVE precisar só de Python. O HTML do relatório já vai pronto no repositório; Node só é preciso para quem desenvolve o frontend.
3. Para a IA, o Rastro DEVE usar a CLI (Kiro, Claude ou Codex) já instalada e autenticada no sistema de quem usa. O Rastro não instala nem autentica CLI.
4. Sem Docker: o requisito do curso ("Docker ou vídeo") é atendido pela gravação do demo.
5. Código, spec, steering, README e relatório NÃO DEVEM depender de arquivo fora do repositório; os entregáveis ficam em `docs/`.

## R21 Travas contra invenção (RF16)

**Como** auditor, **quero** que nada no relatório seja inventado pela IA **para** confiar nele e defendê-lo diante do time.

O princípio: **a IA sugere, a regra confirma.** Toda saída da IA passa por travas determinísticas antes de virar dado do relatório. As travas consultam fontes oficiais só com leitura.

1. O Rastro DEVE exigir da IA um formato fechado (JSON com campos fixos). SE vier campo a mais, campo faltando ou texto fora do JSON, ENTÃO o Rastro DEVE descartar a resposta inteira.
2. **Trecho real:** SE o trecho de evidência devolvido pela IA não for cópia literal de um dos trechos enviados, ENTÃO a biblioteca não é confirmada.
3. **Ancoragem:** SE a versão devolvida não aparecer literalmente no trecho de evidência, ENTÃO a biblioteca não é confirmada.
4. **Pacote existe:** QUANDO uma biblioteca for identificada, por assinatura ou por IA, o Rastro DEVE confirmar no registro do npm, só com leitura, que `pacote@versão` foi publicado. SE não foi, ENTÃO a biblioteca não é confirmada.
5. **Código confere:** QUANDO a biblioteca vier da IA, o Rastro DEVE ler o pacote publicado naquela versão (em memória, sem instalar, extrair em disco nem executar) e conferir que o trecho de evidência aparece no código dele. SE não aparecer, ENTÃO a biblioteca não é confirmada. **[spike]** O critério de comparação sai do teste no Juice Shop.
6. **Explicação sem fato novo:** SE a explicação da IA citar CVE, GHSA, versão ou número que não estava na entrada enviada, ENTÃO o Rastro DEVE descartar a explicação (R07.3).
7. **Faixa conferida:** O Rastro DEVE conferir localmente que a versão está dentro da faixa afetada de cada aviso. SE não estiver, ENTÃO o Rastro DEVE descartar o aviso para aquela biblioteca e registrar o motivo.
8. **Fatos só da fonte:** versão-alvo, CVE, GHSA, CVSS, EPSS, links, nota e prioridade DEVEM vir só do GitHub Advisory, do registro do npm e da fórmula. A IA nunca preenche esses campos.
9. SE o registro do npm não responder, ENTÃO o Rastro DEVE manter a biblioteca por assinatura com o selo "não conferida no npm" e mandar a da IA para "a confirmar".
10. O Rastro DEVE registrar no painel da IA cada vez que uma trava barrar algo: qual trava, o que foi barrado e por quê.

---

## Fora do escopo do MVP

- Scan ativo (envio de ataques) e análise de código-fonte.
- Bibliotecas de back-end: só o que chega ao navegador.
- Outras fontes além de GitHub Advisory, OSV e NVD: CISA KEV, Exploit-DB, Vulners.
- Integração com Azure DevOps ou GitLab: vincular a task e acompanhar no painel.
- Base de falsos positivos por projeto (selo "FP conhecido" e pedido de inclusão).
- Tour guiado e guia animado "Como usar": no MVP, README com prints.
- Execução automática na esteira com Playwright.
- CI e Docker: o Rastro é instalado e verificado na máquina local.

## Planos futuros

Ideias para depois do MVP. Não entram na nota nem no cronograma, mas o design deixa o caminho aberto.

| Plano | Por quê | Ponto de extensão |
|---|---|---|
| **Mais fontes de dados:** OSV e NVD (se não couberem no MVP), CISA KEV (falhas exploradas de fato), Exploit-DB, Vulners | Confirmar exploração real e cobrir avisos que o GitHub ainda não tem | Um arquivo novo em `rastro/fontes/` que implementa `ConectorDeAvisos` (skill `rastro-nova-regra`) |
| **Avaliar integrar o DefectDojo no SD** | Centralizar os achados do Rastro com os das outras ferramentas de segurança e acompanhar a correção num só lugar | O JSON do relatório já tem tudo; falta um exportador para o formato de importação do DefectDojo, em `rastro/relatorio/` |
| Vincular a task no Azure DevOps ou no GitLab e acompanhar no painel | Fechar o ciclo do achado à correção | Hoje a task sai como texto pronto para copiar |
| Base de falsos positivos por projeto | Não repetir a mesma triagem a cada análise | Selo "FP conhecido", já desenhado no demo |
| Rodar na esteira com Playwright | Analisar a cada pipeline, com o HAR gravado pelos testes E2E (`recordHar`) | A CLI já roda sem interação e com `--sem-ia` |
| Tour guiado e guia animado "Como usar" | Ajudar quem usa pela primeira vez | Já desenhados no demo |
