# Tasks: Rastro

**Em que passos.** Tasks pequenas e ordenadas, que o agente executa uma a uma. Cada task:

- cabe em até meio dia;
- vira **um commit**: `<tipo>(<escopo>): <o que muda> (Tnn)`, com o código, os testes e o `[x]` desta lista;
- aponta os critérios do `requirements.md` que atende. O teste leva o ID do critério no nome.

As travas que não dependem da IA (formato, ancoragem, explicação) ficam na fase 1: são regras puras e chegam testadas antes da IA entrar.

Ordem: spike → núcleo determinístico → relatório HTML → explicação por IA → identificação por IA (por último e com prazo limite) → entrega.

| Fase | Semana | Tasks |
|---|---|---|
| 0. Preparar | 09–13/11 | T01–T07 |
| 1. Núcleo determinístico | 16–25/11 | T08–T23 |
| 2. Relatório HTML | 23–28/11 | T24–T32, T54–T57 |
| 3. IA | 30/11–04/12 | T33–T41, T52 |
| 4. Entregar | 04–08/12 | T42–T48 |
| Extensão: OSV e NVD (só se houver tempo) | até 02/12 | T49–T51 |
| Extensão: gravar a visita (branch `feat/gravar`, só se houver tempo) | até 08/12 | T58–T64 |

Meta interna: tudo pronto em 08/12. Entrega: 10/12/2026, 23h59.

## Quem revisa

O Paulo escreve todas as tasks com o agente e é o autor dos commits. Os revisores entram como **coautores** (ver abaixo). A revisão é dividida igualmente entre os outros cinco, **por área**: cada um revisa um bloco que conversa entre si e, por isso, é quem melhor defende aquela parte na banca.

| Revisor | Área | Tasks | Total |
|---|---|---|---|
| @ali.santos | Entrada e identificação: HAR, assinaturas, bundles, instalação, NVD | T03, T05, T08–T11, T40–T42, T50 | 10 |
| @cristiano.albino | Fontes e travas: GitHub Advisory, OSV, npm, travas, privacidade, decisões | T01, T12–T16, T34, T43, T45, T49 | 10 |
| @geison.santos | Risco e ação: nota, prioridade, checagens, plano, task, relatório JSON, junção de fontes | T04, T17–T23, T44, T51 | 10 |
| @halan.bacca | Relatório HTML: frontend, origem do dado, glossário, modo foco, tour e guia | T24–T32, T47, T54, T55 | 12 |
| @luiz.pagliari | IA: CLIs, cliente, provedores, explicação, painel, linha de comando, medição, versão final | T02, T06, T07, T33, T35–T39, T46, T48, T52, T56, T57 | 14 |

## Como cada task chega ao `main`

Direto no `main`, sem branch e sem MR, uma task por vez. A exceção é a extensão "Gravar a visita" (T58–T64), na branch `feat/gravar` (ver o fim desta lista):

1. **Antes do commit:** `ruff check`, `mypy rastro` e `pytest` passam na máquina local.
2. **Um commit por task**, autocontido (funciona sozinho), com o código, os testes, o `[x]` nesta lista e o cartão movido para "Em revisão" no kanban. Push logo depois.
3. **O revisor da task é coautor desde o commit:** a mensagem termina com a linha `Co-authored-by:` dele, e o GitLab e o GitHub mostram os dois nomes:

   ```
   feat(risco): calcular nota de risco pela fórmula fixa (T17)

   Co-authored-by: Geison dos Santos <geison.santos@sc.senai.br>
   ```

4. **Revisão depois do commit:** o revisor abre o commit (`git show <hash>`), confere o critério de aceite e roda a verificação. Ajuste pedido vira um commit novo, `fix(<escopo>): <o que corrige> (T17)`, com o mesmo coautor. Commit já enviado nunca é reescrito (sem `amend`, `rebase` ou `push --force`).
5. **Aprovado:** o cartão vai para "Feito" no próximo commit que for feito (de task ou de ajuste). Não precisa de commit só para isso.

   Os e-mails ficam na tabela abaixo. Eles precisam ser os mesmos que cada pessoa usa no Git, senão o commit não é ligado à conta dela. O autor dos commits é o Paulo (`paulo.mafioletti@sc.senai.br`).

| Revisor | Linha de coautoria |
|---|---|
| @ali.santos | `Co-authored-by: Ali Castilho Santos <ali.santos@sc.senai.br>` |
| @cristiano.albino | `Co-authored-by: Cristiano Gomes Albino <cristiano.albino@sc.senai.br>` |
| @geison.santos | `Co-authored-by: Geison dos Santos <geison.santos@sc.senai.br>` |
| @halan.bacca | `Co-authored-by: Halan Germano Bacca <halan.bacca@sc.senai.br>` |
| @luiz.pagliari | `Co-authored-by: Luiz Gabriel Pagliari Moreira <luiz.pagliari@sc.senai.br>` |

O estado de cada task (a fazer, em andamento, em revisão, feito) fica no `kanban.md`, ao lado deste arquivo. O cartão anda no mesmo commit da task.

Assim, o histórico levado para a org SENAI-IA conta a construção task por task, e cada commit diz quem revisou (na linha de coautoria).

---

## Fase 0. Preparar

- [x] **T01 Validar o GitHub Advisory e o EPSS**
  - Entrega: registro do spike com limite sem token, formato de `epss` e `cvss_severities` e taxa de EPSS vazio em 20 pacotes.
  - Aceite: as perguntas da seção 17 do design sobre a fonte estão respondidas; o design e os critérios [spike] de R04 e R05 estão ajustados.
  - Arquivos: `docs/spike/github-advisory.md`, `design.md`, `requirements.md`
  - Teste: não se aplica (exploração).
  - Requisito: R04.1, R04.4, R05.3
  - Revisão: @cristiano.albino

- [x] **T02 Validar as CLIs de IA sem interação**
  - Entrega: comando, formato da resposta e tokens de Kiro, Claude e Codex, com o prompt pela entrada padrão, no Linux. O Windows é conferido na T42, com a lista do spike.
  - Aceite: a tabela de provedores do design está preenchida, com o que funciona e o que não funciona no Linux e o que falta conferir no Windows.
  - Arquivos: `docs/spike/clis-de-ia.md`, `design.md`
  - Teste: não se aplica (exploração).
  - Requisito: R14.4, R18.1
  - Revisão: @luiz.pagliari

- [x] **T03 Validar o HAR real e o bundle do Juice Shop**
  - Entrega: HAR exportado do Chrome (completo e sanitized) e prova de identificação de um bundle pela IA, à mão.
  - Aceite: está registrado se o HAR traz o conteúdo dos scripts, o que o sanitized remove, o tamanho dos bundles, se a IA acerta nome e versão e qual critério da trava 5 (trecho × código publicado no npm) acerta sem deixar passar invenção.
  - Arquivos: `docs/spike/har-e-bundles.md`, `design.md`
  - Teste: não se aplica (exploração).
  - Requisito: R01.1, R03.1, R06.7, R21.5
  - Revisão: @ali.santos

- [x] **T04 Montar a avaliação**
  - Entrega: HARs das aplicações-alvo e o gabarito com as bibliotecas e versões reais de cada uma.
  - Aceite: pelo menos dois alvos com bibliotecas vulneráveis reais, além do Juice Shop (o front-end dele não tem falha conhecida, spike T03); o gabarito diz quais estão em bundle; o HAR sanitized e o completo exportados do Chrome conferidos pela lista "A conferir no Chrome" de `docs/spike/har-e-bundles.md`.
  - Arquivos: `avaliacao/README.md`, `avaliacao/gabarito.json`, `avaliacao/*.har` (só HAR sanitized no repo)
  - Teste: não se aplica.
  - Requisito: métricas do PRD
  - Revisão: @geison.santos

- [x] **T05 Criar o esqueleto Python**
  - Entrega: pacote `rastro` com `python -m rastro --help`, `requirements-dev.txt` e a configuração de `ruff`, `mypy` e `pytest` no `pyproject.toml`.
  - Aceite: `pip install -r requirements-dev.txt`, `ruff check`, `mypy rastro` e `pytest` passam no Linux e no Windows; um `conftest.py` bloqueia qualquer acesso à rede nos testes.
  - Arquivos: `pyproject.toml`, `requirements-dev.txt`, `rastro/__init__.py`, `rastro/__main__.py`, `rastro/cli.py`, `tests/test_cli.py`
  - Teste: `test_cli.py` (ajuda abre e retorna 0)
  - Requisito: R18.1, R19.2, R19.3
  - Revisão: @ali.santos

- [x] **T06 Documentar a verificação local**
  - Entrega: seção "Verificação" no README com `ruff check`, `mypy rastro` e `pytest --cov`, para Windows e Linux.
  - Aceite: os três comandos passam no Linux e no Windows, na máquina local, e o resultado de cada sistema fica em `docs/cobertura/`.
  - Arquivos: `README.md`, `docs/cobertura/`
  - Teste: os próprios comandos.
  - Requisito: R18.2, R19.3
  - Revisão: @luiz.pagliari

- [x] **T07 Escrever a skill `rastro-nova-regra`**
  - Entrega: passo a passo para acrescentar checagem, assinatura, fonte, provedor de IA ou trava, com o teste e a cobertura esperados.
  - Aceite: a skill é usada de verdade em T10 e T19 (conferido nessas tasks).
  - Arquivos: `.kiro/skills/rastro-nova-regra/SKILL.md`
  - Teste: não se aplica.
  - Requisito: entregável do curso
  - Revisão: @luiz.pagliari

## Fase 1. Núcleo determinístico

- [x] **T08 Ler e validar o HAR**
  - Entrega: `ler_har(caminho)` devolve a lista de `Requisicao`.
  - Aceite: lê HAR válido, decodifica base64 e falha com mensagem clara para arquivo ausente ou inválido.
  - Arquivos: `rastro/har/leitor.py`, `rastro/har/modelos.py`, `tests/har/test_leitor.py`, `tests/dados/*.har`
  - Teste: `test_r01_*`
  - Requisito: R01.1–R01.5
  - Revisão: @ali.santos

- [x] **T09 Descobrir o site analisado**
  - Entrega: `descobrir_site_analisado(requisicoes)` devolve o host da primeira resposta HTML.
  - Aceite: funciona com redirecionamento e com HAR sem HTML (devolve `None`).
  - Arquivos: `rastro/har/site.py`, `tests/har/test_site.py`
  - Teste: `test_r01_7_*`
  - Requisito: R01.7
  - Revisão: @ali.santos

- [x] **T10 Identificar bibliotecas pelo nome do arquivo**
  - Entrega: tabela de assinaturas e reconhecimento pela URL.
  - Aceite: reconhece as bibliotecas mínimas de R02.4 por URL de arquivo, de CDN (`@versão`) e com `?v=` (`ckeditor.js?v=4.10.1`).
  - Arquivos: `rastro/identificacao/assinaturas.py`, `rastro/identificacao/modelos.py`, `tests/identificacao/test_assinaturas.py`
  - Teste: `test_r02_1_*`, `test_r02_4_*`
  - Requisito: R02.1, R02.4, R02.5
  - Revisão: @ali.santos

- [x] **T11 Identificar bibliotecas pelo comentário de versão**
  - Entrega: reconhecimento pelo comentário no conteúdo inteiro, a partir do início do comentário, e agrupamento das repetidas.
  - Aceite: a mesma biblioteca em duas requisições aparece uma vez, com duas evidências; um bundle com vários comentários registra cada biblioteca; `Requires jQuery v1.7.2` não vira jQuery; com nome e comentário divergentes, vale o comentário (casos do `avaliacao/gabarito.json`).
  - Arquivos: `rastro/identificacao/assinaturas.py`, `tests/identificacao/test_assinaturas.py`
  - Teste: `test_r02_2_*`, `test_r02_3_*`
  - Requisito: R02.2, R02.3
  - Revisão: @ali.santos

- [x] **T12 Consultar o GitHub Advisory**
  - Entrega: `ConectorDeAvisos` e `GitHubAdvisory.consultar(pacote, versao)`.
  - Aceite: converte uma resposta gravada em `Aviso`; usa o token quando existe; erro de rede vira "não consultada"; descarta aviso retirado; CVSS com `score: 0.0` e vetor nulo conta como ausente; sem a chave `epss`, o percentil fica `None`.
  - Arquivos: `rastro/fontes/conector.py`, `rastro/fontes/github_advisory.py`, `tests/fontes/test_github_advisory.py`, `tests/dados/advisory-*.json`
  - Teste: `test_r04_*` (com `urlopen` trocado por dublê)
  - Requisito: R04.1–R04.6
  - Revisão: @cristiano.albino

- [x] **T13 Conferir a faixa de versão afetada**
  - Entrega: trava `faixa_de_versao.py`, aplicada a cada aviso.
  - Aceite: `>= 1.2.0, < 3.5.0` contém 3.4.1 e não contém 3.5.0; pré-lançamento é menor que a final; aviso fora da faixa é descartado e registrado.
  - Arquivos: `rastro/travas/faixa_de_versao.py`, `rastro/travas/modelos.py`, `tests/travas/test_faixa_de_versao.py`
  - Teste: `test_r21_7_*`
  - Requisito: R21.7
  - Revisão: @cristiano.albino

- [x] **T14 Conferir no npm se o pacote existe**
  - Entrega: `RegistroDePacotes`, `registro_npm.existe(pacote, versao)` e a trava 4 aplicada às bibliotecas por assinatura.
  - Aceite: 200 confirma, 404 manda para "a confirmar", sem rede dá "não conferida no npm"; pacote com escopo usa `%2F`.
  - Arquivos: `rastro/fontes/registro_npm.py`, `rastro/travas/conferencia.py`, `tests/fontes/test_registro_npm.py`, `tests/travas/test_conferencia.py`
  - Teste: `test_r21_4_*`, `test_r21_9_*` (com `urlopen` trocado por dublê)
  - Requisito: R21.4, R21.9, R16.2
  - Revisão: @cristiano.albino

- [x] **T15 Travar a resposta da IA: formato e ancoragem**
  - Entrega: travas `formato.py` e `ancoragem.py`.
  - Aceite: JSON com campo a mais ou texto fora dele é descartado; trecho não enviado ou versão ausente do trecho manda a biblioteca para "a confirmar".
  - Arquivos: `rastro/travas/formato.py`, `rastro/travas/ancoragem.py`, `tests/travas/test_formato.py`, `tests/travas/test_ancoragem.py`
  - Teste: `test_r21_1_*`, `test_r21_2_*`, `test_r21_3_*`
  - Requisito: R21.1–R21.3
  - Revisão: @cristiano.albino

- [x] **T16 Barrar explicação com fato novo**
  - Entrega: trava `travas/explicacao.py`.
  - Aceite: explicação que cita CVE, GHSA, versão ou porcentagem fora da entrada é descartada; a que só repete a entrada passa.
  - Arquivos: `rastro/travas/explicacao.py`, `tests/travas/test_explicacao.py`
  - Teste: `test_r21_6_*`
  - Requisito: R21.6, R21.8
  - Revisão: @cristiano.albino

- [x] **T17 Calcular a nota de risco**
  - Entrega: `calcular_nota_de_risco` e os casos sem EPSS e sem CVSS, com a conta escrita.
  - Aceite: CVSS 6,1 e percentil 0,97 dão 7,9; sem EPSS usa o CVSS; sem CVSS dá "sem nota".
  - Arquivos: `rastro/risco/nota.py`, `tests/risco/test_nota.py`
  - Teste: `test_r05_1_*`, `test_r05_3_*`, `test_r05_4_*`
  - Requisito: R05.1, R05.3, R05.4, R10.1
  - Revisão: @geison.santos

- [x] **T18 Classificar a prioridade e ordenar**
  - Entrega: faixas, nota da biblioteca e ordem dos achados.
  - Aceite: 7,5 é alta, 7,4 é média, 6,5 é média, 6,4 é baixa; empate desfeito pelo CVSS.
  - Arquivos: `rastro/risco/prioridade.py`, `tests/risco/test_prioridade.py`
  - Teste: `test_r05_2_*`, `test_r05_5_*`, `test_r05_6_*`
  - Requisito: R05.2, R05.5, R05.6, R05.7
  - Revisão: @geison.santos

- [x] **T19 Checar os cabeçalhos de segurança**
  - Entrega: checagens C01 a C05, uma função cada.
  - Aceite: cada checagem tem um caso que falha e um que passa; só olha respostas do site analisado.
  - Arquivos: `rastro/configuracao/checagens.py`, `rastro/configuracao/modelos.py`, `tests/configuracao/test_checagens.py`
  - Teste: `test_r06_1_*` a `test_r06_5_*`, `test_r06_8_*`
  - Requisito: R06.1–R06.5, R06.8
  - Revisão: @geison.santos

- [x] **T20 Checar os cookies**
  - Entrega: checagens C06 a C08 e o estado "não verificada".
  - Aceite: HAR sanitized dá "não verificada"; o valor do cookie nunca aparece no resultado.
  - Arquivos: `rastro/configuracao/checagens.py`, `tests/configuracao/test_checagens.py`
  - Teste: `test_r06_6_*`, `test_r06_7_*`
  - Requisito: R06.6, R06.7, R16.4, R16.5
  - Revisão: @geison.santos

- [x] **T21 Montar o plano de ação**
  - Entrega: `montar_plano_de_acao(achados, explicacoes, checagens)`.
  - Aceite: uma ação por biblioteca vulnerável e por checagem com falha, com a versão-alvo certa e o caso "sem correção publicada".
  - Arquivos: `rastro/acao/plano.py`, `rastro/acao/modelos.py`, `tests/acao/test_plano.py`
  - Teste: `test_r08_*`
  - Requisito: R08.1–R08.5
  - Revisão: @geison.santos

- [x] **T22 Gerar o texto da task**
  - Entrega: `gerar_texto_da_task(acao)` em Markdown, pelo modelo do design.
  - Aceite: o texto tem título, por quê, impacto, o que fazer, critério de aceite e checklist; funciona sem explicação da IA.
  - Arquivos: `rastro/acao/task.py`, `tests/acao/test_task.py`
  - Teste: `test_r09_1_*`
  - Requisito: R09.1
  - Revisão: @geison.santos

- [x] **T23 Gravar o relatório JSON e ligar o fluxo sem IA**
  - Entrega: `fluxo.analisar`, `relatorio/json.py`, `relatorio/gravacao.py` e o comando `analisar --sem-ia` de ponta a ponta.
  - Aceite: `python -m rastro analisar tests/dados/loja.har --sem-ia` grava `relatorio.json` em `~/Rastro/relatorios/<site>/<AAAA-MM-DD_HH-MM-SS>/` (ou em `--saida`), com `resumo` e `limitacoes` preenchidos, e avisa no terminal que a análise está incompleta; com a pasta da análise já existente, para sem gravar; nomes de pasta válidos no Windows.
  - Arquivos: `rastro/fluxo.py`, `rastro/cli.py`, `rastro/relatorio/json.py`, `rastro/relatorio/gravacao.py`, `tests/test_fluxo.py`, `tests/relatorio/*`
  - Teste: `test_r13_1_*` a `test_r13_4_*`, `test_r13_7_*`, `test_r13_8_*`, `test_r14_5_*`, `test_r14_7_*`, `test_r16_1_*`, `test_r16_4_*`, `test_r17_1_*`
  - Requisito: R01.6, R13.1–R13.4, R13.7, R13.8, R14.5, R14.7, R16.1, R16.4, R17.1
  - Revisão: @geison.santos

## Fase 2. Relatório HTML

- [x] **T24 Criar o projeto do frontend**
  - Entrega: React + TypeScript (template do Vite) com `vite-plugin-singlefile`, `tokens.css` claro e escuro e `tipos.ts`.
  - Aceite: `npm run build` gera um único `index.html` que lê o JSON da tag `dados`.
  - Arquivos: `frontend/*`
  - Teste: o build roda sem erro.
  - Requisito: R13.5, R13.6
  - Revisão: @halan.bacca

- [x] **T25 Embutir o JSON no HTML**
  - Entrega: `relatorio/html.py` gera o `relatorio.html` a partir do modelo do build.
  - Aceite: o relatório abre com duplo clique e sem rede; `</script>` dentro dos dados não quebra a página.
  - Arquivos: `rastro/relatorio/html.py`, `rastro/relatorio/modelo.html`, `tests/relatorio/test_html.py`
  - Teste: `test_r13_5_*`
  - Requisito: R13.1, R13.5
  - Revisão: @halan.bacca

- [x] **T26 Mostrar os indicadores e o plano de ação**
  - Entrega: `BarraSuperior`, `CabecalhoAnalise`, `Indicador`, `PlanoDeAcao`, `Acao`, `Selo`, `Icone`.
  - Aceite: a tela mostra os quatro indicadores e as ações na ordem do JSON, em claro, escuro e 400px. *(verificação manual)*
  - Arquivos: `frontend/src/App.tsx`, `frontend/src/componentes/*`
  - Teste: verificação manual.
  - Requisito: R08.3, R13.6
  - Revisão: @halan.bacca

- [x] **T27 Mostrar o aviso de análise sem IA**
  - Entrega: componente `AvisoSemIA` e o indicador "encontradas só pela IA" como "não procurado".
  - Aceite: com `limitacoes` preenchido, a faixa aparece no topo e continua visível ao rolar; sem limitações, não aparece. *(verificação manual)*
  - Arquivos: `frontend/src/componentes/AvisoSemIA.*`, `frontend/src/App.tsx`
  - Teste: verificação manual.
  - Requisito: R14.6
  - Revisão: @halan.bacca

- [x] **T28 Mostrar bibliotecas, falhas e checagens**
  - Entrega: `ListaBibliotecas`, `LinhaBiblioteca`, `ListaFalhas`, `ItemFalha`, `ListaChecagens`, `ItemChecagem`, com detalhes recolhidos.
  - Aceite: selos "sem EPSS", "não consultada", "não conferida no npm" e "não verificada" aparecem quando o JSON traz o estado; a lista "a confirmar" fica separada, com a trava que falhou e como confirmar à mão. *(verificação manual)*
  - Arquivos: `frontend/src/componentes/*`
  - Teste: verificação manual.
  - Requisito: R03.4, R04.3, R05.3, R06.7, R21.9
  - Revisão: @halan.bacca

- [x] **T29 Mostrar a origem de cada dado**
  - Entrega: `PainelOrigemDoDado` com HAR → identificação → aviso → cálculo.
  - Aceite: clique em biblioteca, falha ou nota abre o painel com a conta escrita. *(verificação manual)*
  - Arquivos: `frontend/src/componentes/PainelOrigemDoDado.*`
  - Teste: verificação manual.
  - Requisito: R10.2
  - Revisão: @halan.bacca

- [x] **T30 Mostrar o glossário**
  - Entrega: `Termo`, `Dica` e `dados/glossario.ts`.
  - Aceite: definição aparece com mouse, teclado e toque. *(verificação manual)*
  - Arquivos: `frontend/src/componentes/Termo.*`, `Dica.*`, `frontend/src/dados/glossario.ts`
  - Teste: verificação manual.
  - Requisito: R12.1, R12.2
  - Revisão: @halan.bacca

- [x] **T31 Abrir e copiar a task**
  - Entrega: `ModalTask` com o texto da task e botão de copiar.
  - Aceite: o texto copiado é igual ao do JSON. *(verificação manual)*
  - Arquivos: `frontend/src/componentes/ModalTask.*`
  - Teste: verificação manual.
  - Requisito: R09.2
  - Revisão: @halan.bacca

- [x] **T32 Ler uma zona por vez (modo foco)**
  - Entrega: estado `zonaEmFoco` no `App`, botão "Focar" em cada zona e `BarraDeFoco`.
  - Aceite: o relatório abre como hoje; cada zona entra em foco e sai com Esc ou botão; painel de origem, glossário e task funcionam em foco; teclado e 400px conferidos. *(verificação manual)*
  - Arquivos: `frontend/src/App.tsx`, `frontend/src/componentes/BarraDeFoco.*`
  - Teste: verificação manual.
  - Requisito: R15.1–R15.7
  - Revisão: @halan.bacca

- [x] **T54 Rever a visita num radar**
  - Entrega: `har/visita.py` e a `visita` no JSON; no relatório, `ReplayDaVisita` e `RadarDaVisita` na zona Rastreado, a partir da POC aprovada pelo time (branch `poc/replay-do-rastro`, que não vai para o `main`).
  - Aceite: o JSON do WebGoat traz a visita em ordem, com camada, bibliotecas e prioridade; o radar toca, pausa, recomeça e abre a biblioteca nos Detalhes; cabe na primeira dobra em 1366×768 e 1280×720, também em foco; claro, escuro e 400px conferidos; sem animação com `prefers-reduced-motion`. *(verificação manual na tela)*
  - Arquivos: `rastro/har/modelos.py`, `rastro/har/leitor.py`, `rastro/har/visita.py`, `rastro/fluxo.py`, `rastro/relatorio/json.py`, `rastro/relatorio/modelo.html`, `tests/har/test_leitor.py`, `tests/har/test_visita.py`, `tests/relatorio/test_json.py`, `frontend/src/App.tsx`, `frontend/src/tipos.ts`, `frontend/src/componentes/ReplayDaVisita.*`, `frontend/src/componentes/RadarDaVisita.*`, `frontend/src/componentes/{usarRelogioDoReplay,usarAlturaAteADobra,chegadasDaVisita,geometriaDoRadar}.ts`, `frontend/src/componentes/Icone.tsx`, `frontend/src/componentes/LinhaBiblioteca.tsx`, `.kiro/steering/structure.md`, `.kiro/steering/frontend-react.md`
  - Teste: `test_r22_1_*` a `test_r22_3_*`; o radar, verificação manual.
  - Requisito: R22.1–R22.8
  - Revisão: @halan.bacca

- [x] **T55 Ensinar a usar o relatório: tour guiado e Como usar**
  - Entrega: `TourGuiado`, `posicaoDoTour.ts` e `dados/tour.ts`; `GuiaComoUsar`, `PassoDoGuia`, `IlustracaoDoGuia` e `dados/guia.ts`; botões "Tour guiado" e "Painel" / "Como usar" na `BarraSuperior`, a partir do esboço visual do planejamento, refeito para a tela de hoje.
  - Aceite: o relatório abre no painel; o tour passa só pelas partes que existem (conferido com o WebGoat, com o Juice Shop e com uma análise sem IA), anda por teclado e devolve o foco ao fechar; o guia mostra os sete passos com ilustração, "Marcar como feito" e progresso; claro, escuro, 400px e `prefers-reduced-motion` conferidos. *(verificação manual na tela)*
  - Arquivos: `frontend/src/App.tsx`, `frontend/src/componentes/BarraSuperior.*`, `frontend/src/componentes/TourGuiado.*`, `frontend/src/componentes/posicaoDoTour.ts`, `frontend/src/componentes/GuiaComoUsar.*`, `frontend/src/componentes/PassoDoGuia.*`, `frontend/src/componentes/IlustracaoDoGuia.*`, `frontend/src/componentes/TextoComMarcas.tsx`, `frontend/src/componentes/Icone.tsx`, `frontend/src/dados/tour.ts`, `frontend/src/dados/guia.ts`, `rastro/relatorio/modelo.html`, `.kiro/steering/frontend-react.md`, `.kiro/steering/product.md`, `README.md`, `docs/prints/11-tour-guiado.png`, `docs/prints/12-como-usar.png`
  - Teste: verificação manual.
  - Requisito: R23.1–R23.7
  - Revisão: @halan.bacca

- [x] **T56 Abrir o Como usar pela linha de comando**
  - Entrega: o comando `python -m rastro como-usar` abre no navegador o relatório sem dados, que passa a começar na tela "Como usar".
  - Aceite: `como-usar` abre o `modelo.html` do pacote e mostra o caminho, sem ler HAR, sem rede e sem gravar; sem navegador, avisa e mostra o caminho com código 0; o `--help` lista o comando; o relatório com análise continua abrindo no painel. Teste com o navegador trocado por dublê.
  - Arquivos: `rastro/cli.py`, `rastro/relatorio/html.py`, `tests/test_cli.py`, `frontend/src/App.tsx`, `rastro/relatorio/modelo.html`, `README.md`
  - Teste: `test_r23_8_*`; o resto, verificação manual.
  - Requisito: R23.1, R23.8
  - Revisão: @luiz.pagliari

- [x] **T57 Rodar o Rastro de qualquer pasta**
  - Entrega: a pessoa cria o comando `rastro` com `python -m rastro instalar`, uma vez, na raiz do projeto, e remove com `rastro desinstalar`; o comando roda `analisar` e `como-usar` de qualquer pasta. O `pyproject.toml` também permite `pipx install .`.
  - Aceite: `instalar` grava o atalho marcado na pasta do usuário, com o Python do sistema mesmo com o `.venv` ativo, e põe a pasta no PATH só se faltar, sem repetir o bloco; num terminal novo, `rastro --help` funciona fora da pasta do projeto; `desinstalar` remove só o atalho e o bloco marcados; um `rastro` sem a marca não é tocado e o comando sai com 1; o pacote montado do projeto cria o comando `rastro` e leva o `modelo.html` e os prompts; `python -m rastro` na raiz continua igual; README e README técnico com o passo a passo no Linux e no Windows (Windows a conferir na T42).
  - Arquivos: `pyproject.toml`, `requirements-dev.txt`, `rastro/atalho.py`, `rastro/cli.py`, `rastro/__main__.py`, `tests/test_atalho.py`, `tests/test_cli.py`, `tests/test_instalacao.py`, `README.md`, `README-TECNICO.md`, `.kiro/steering/tech.md`, `.kiro/steering/structure.md`
  - Teste: `test_r17_3_*` e `test_r18_1_*`: instala e desinstala numa pasta de usuário falsa (`tmp_path`) e roda o atalho de outra pasta; monta o pacote sem rede (`pip wheel --no-build-isolation --no-index`) e confere o comando e os arquivos de dados; `principal()` sai com o código da execução. O PATH do Windows (registro), verificação manual na T42.
  - Requisito: R17.3, R18.1, R20.1
  - Revisão: @luiz.pagliari

## Fase 3. IA

- [x] **T33 Criar o cliente de IA e a escolha do provedor**
  - Entrega: `ProvedorDeIA`, `ClienteDeIA` e a escolha por `--ia`, `RASTRO_IA` ou padrão.
  - Aceite: com `ProvedorFalso`, cada chamada fica registrada com tempo e tokens; IA inválida ou CLI ausente encerram com código 1.
  - Arquivos: `rastro/ia/cliente.py`, `rastro/cli.py`, `tests/ia/test_cliente.py`
  - Teste: `test_r11_1_*`, `test_r11_2_*`, `test_r14_1_*` a `test_r14_3_*`, `test_r14_8_*`
  - Requisito: R11.1, R11.2, R14.1–R14.3, R14.8
  - Revisão: @luiz.pagliari

- [x] **T34 Tirar dados sensíveis do que vai para a IA**
  - Entrega: `ia/sanitizacao.py`.
  - Aceite: JWT, `Bearer`, chaves longas e query strings viram `[removido]`.
  - Arquivos: `rastro/ia/sanitizacao.py`, `tests/ia/test_sanitizacao.py`
  - Teste: `test_r16_3_*`
  - Requisito: R16.3
  - Revisão: @cristiano.albino

- [x] **T35 Chamar o Claude pela CLI**
  - Entrega: `provedores/claude.py`.
  - Aceite: prompt pela entrada padrão, tokens lidos da resposta; teste com `subprocess.run` trocado por dublê.
  - Arquivos: `rastro/ia/provedores/claude.py`, `tests/ia/provedores/test_claude.py`
  - Teste: `test_r14_4_*`
  - Requisito: R14.4
  - Revisão: @luiz.pagliari

- [x] **T36 Chamar o Codex pela CLI**
  - Entrega: `provedores/codex.py`.
  - Aceite: igual à T35, com o formato do Codex.
  - Arquivos: `rastro/ia/provedores/codex.py`, `tests/ia/provedores/test_codex.py`
  - Teste: `test_r14_4_*`
  - Requisito: R14.4
  - Revisão: @luiz.pagliari

- [x] **T37 Chamar o Kiro pela CLI**
  - Entrega: `provedores/kiro.py`.
  - Aceite: igual à T35, com o formato do Kiro.
  - Arquivos: `rastro/ia/provedores/kiro.py`, `tests/ia/provedores/test_kiro.py`
  - Teste: `test_r14_4_*`
  - Requisito: R14.4
  - Revisão: @luiz.pagliari

- [x] **T38 Explicar cada achado com IA**
  - Entrega: prompt `explicar_achado.md` e `explicacao/ia.py`, ligados ao fluxo e à task.
  - Aceite: resposta válida vira `Explicacao` marcada como IA; resposta inválida usa o resumo do aviso e o selo "sem explicação da IA".
  - Arquivos: `rastro/ia/prompts/explicar_achado.md`, `rastro/explicacao/ia.py`, `rastro/fluxo.py`, `tests/explicacao/test_ia.py`
  - Teste: `test_r07_*`
  - Requisito: R07.1–R07.4
  - Revisão: @luiz.pagliari

- [x] **T39 Mostrar onde a IA entrou**
  - Entrega: contagem com IA × sem IA no JSON e os componentes `PainelIA` e `ExplicacaoIA`.
  - Aceite: o painel mostra chamadas, entrada, resposta, tempo e tokens, ou "não informado" quando faltar; numa análise sem IA, mostra "IA desligada nesta análise"; lista as travas acionadas, com o que barraram e por quê.
  - Arquivos: `rastro/relatorio/json.py`, `frontend/src/componentes/PainelIA.*`, `ExplicacaoIA.*`, `tests/relatorio/test_json.py`
  - Teste: `test_r11_3_*`, `test_r21_10_*`
  - Requisito: R11.3, R21.10
  - Revisão: @luiz.pagliari

- [x] **T40 Conferir o trecho no código publicado**
  - Entrega: leitura do `.tgz` do npm em memória (com conferência de integridade) e trava `codigo_publicado.py`.
  - Aceite: trecho real do pacote passa; trecho inventado não passa; nada é extraído em disco nem executado; pacote acima de 10 MB fica "a confirmar".
  - Arquivos: `rastro/fontes/registro_npm.py`, `rastro/travas/codigo_publicado.py`, `tests/fontes/test_registro_npm.py`, `tests/travas/test_codigo_publicado.py`
  - Teste: `test_r21_5_*` (`.tgz` montado no teste, sem rede)
  - Requisito: R21.5
  - Revisão: @ali.santos

- [x] **T41 Identificar bibliotecas em bundles com IA** · prazo limite 04/12
  - Entrega: `bundles.py`, prompt `identificar_bibliotecas.md` e `identificacao/ia.py`.
  - Aceite: no HAR do Juice Shop, confirma ao menos uma biblioteca do gabarito que a assinatura não vê; toda biblioteca da IA passa pelas travas 1 a 6 antes de entrar no relatório.
  - Arquivos: `rastro/identificacao/bundles.py`, `rastro/identificacao/ia.py`, `rastro/ia/prompts/identificar_bibliotecas.md`, `tests/identificacao/test_bundles.py`, `tests/identificacao/test_ia.py`
  - Teste: `test_r03_*`
  - Requisito: R03.1–R03.5, R21.8
  - Revisão: @ali.santos

- [x] **T52 Ligar a IA na linha de comando**
  - Entrega: o `cli.py` monta o `ClienteDeIA` com o provedor escolhido (`--ia`, `RASTRO_IA` ou Kiro) e passa ao `fluxo.analisar`; sai a mensagem "ainda não está disponível".
  - Aceite: `analisar` sem `--sem-ia`, com a CLI instalada, gera o relatório com a IA (identificação em bundles, explicações e chamadas no JSON); IA inválida ou CLI ausente seguem em código 1; teste com o provedor trocado por dublê.
  - Arquivos: `rastro/cli.py`, `tests/test_cli.py`, `design.md`
  - Teste: `test_r14_*`
  - Requisito: R14.1–R14.4, R14.8
  - Revisão: @luiz.pagliari

## Fase 4. Entregar

- [ ] **T42 Instalar do zero no Windows e no Linux**
  - Entrega: instalação conferida numa máquina limpa de cada sistema, só com Python e a CLI de IA já instalada.
  - Aceite: seguindo só o README, gera o relatório com IA e com `--sem-ia`, sem Node e sem instalar nada global; o comando `rastro` criado com `py -m rastro instalar` (T57) roda de outra pasta e o `rastro desinstalar` o remove; no Windows, a lista "A conferir no Windows" de `docs/spike/clis-de-ia.md` está conferida e a coluna Windows da tabela de provedores do design, preenchida.
  - Arquivos: `README.md` (ajustes que aparecerem), `docs/spike/clis-de-ia.md`, `design.md`
  - Teste: verificação manual.
  - Requisito: R14.4, R17.2, R18.1, R20.1–R20.3
  - Revisão: @ali.santos

- [x] **T43 Escrever o README de uso**
  - Entrega: instalação, uso e roteiro de verificação manual, com comandos Windows e Linux lado a lado e prints; seção "Desenvolvido com IA".
  - Aceite: outra pessoa do grupo segue o README do zero e gera o relatório.
  - Arquivos: `README.md`, `docs/prints/*`
  - Teste: verificação manual.
  - Requisito: R20.1–R20.4
  - Revisão: @cristiano.albino

- [x] **T44 Publicar o relatório de cobertura**
  - Entrega: relatório HTML do `pytest-cov` em `docs/cobertura/`.
  - Aceite: regras de negócio ≥ 60% (meta 80%); o número está no README.
  - Arquivos: `docs/cobertura/*`, `README.md`
  - Teste: `pytest --cov`
  - Requisito: R19.1
  - Revisão: @geison.santos

- [x] **T45 Registrar as decisões**
  - Entrega: um arquivo por decisão da seção 16 do design.
  - Aceite: cada arquivo tem contexto, decisão e alternativas.
  - Arquivos: `docs/decisoes/*.md`
  - Teste: não se aplica.
  - Requisito: entregável do curso
  - Revisão: @cristiano.albino

- [ ] **T46 Medir com e sem IA**
  - Entrega: tempo de triagem manual × Rastro, bibliotecas e falhas com e sem IA, tokens e tempo por provedor.
  - Aceite: números reais no README e no pitch, no lugar dos ilustrativos; **nenhuma biblioteca confirmada fora do gabarito** (falso positivo confirmado = 0) e quantas sugestões da IA cada trava barrou.
  - Arquivos: `avaliacao/resultados.md`, `README.md`, `docs/pitch-inicial.pdf`
  - Teste: não se aplica.
  - Requisito: métricas do PRD
  - Revisão: @luiz.pagliari

- [ ] **T47 Gravar a apresentação e o demo**
  - Entrega: apresentação de slides narrada e demo do HAR exportado ao relatório e à task aberta.
  - Aceite: links das gravações no README.
  - Arquivos: `README.md`
  - Teste: não se aplica.
  - Requisito: entregável do curso
  - Revisão: @halan.bacca

- [ ] **T48 Preparar a versão final**
  - Entrega: PRD final em `docs/prd.pdf`, com o pitch já em `docs/` e o logo em `frontend/src/assets/`; a spec, o steering e o README citam só esses arquivos.
  - Aceite: código, spec, steering e README só citam arquivos que estão no repositório; build, `ruff`, `mypy` e `pytest` passam.
  - Arquivos: `docs/prd.pdf`, `frontend/src/assets/*`, `.kiro/steering/*`, `.kiro/specs/rastro/*`, `README.md`
  - Teste: verificação local completa.
  - Requisito: R20.5
  - Revisão: @luiz.pagliari

## Extensão: OSV e NVD (só se houver tempo)

Começa só se as fases 1 e 2 estiverem fechadas. Prazo limite: 02/12. O que não fechar vai para os planos futuros, e a análise segue só com o GitHub Advisory.

- [x] **T49 Consultar o OSV**
  - Entrega: `fontes/osv.py` implementando `ConectorDeAvisos` e a leitura da faixa `SEMVER` do OSV.
  - Aceite: converte uma resposta gravada do OSV em `Aviso` com apelidos; falha do OSV não para a análise.
  - Arquivos: `rastro/fontes/osv.py`, `rastro/travas/faixa_de_versao.py`, `tests/fontes/test_osv.py`, `tests/dados/osv-*.json`
  - Teste: `test_r04a_1_*`, `test_r04a_6_*`
  - Requisito: R04A.1, R04A.6
  - Revisão: @cristiano.albino

- [x] **T50 Completar o CVSS pelo NVD**
  - Entrega: `fontes/nvd.py`, chamado só para aviso com CVE e sem CVSS.
  - Aceite: aviso sem CVSS ganha o do NVD, com a fonte registrada; usa `NVD_API_KEY` quando existe; uma consulta por CVE.
  - Arquivos: `rastro/fontes/nvd.py`, `tests/fontes/test_nvd.py`, `tests/dados/nvd-*.json`
  - Teste: `test_r04a_2_*`, `test_r04a_7_*`
  - Requisito: R04A.2, R04A.6, R04A.7
  - Revisão: @ali.santos

- [x] **T51 Juntar avisos de fontes diferentes**
  - Entrega: `fontes/juncao.py` (puro) ligado ao fluxo.
  - Aceite: o mesmo aviso no GitHub e no OSV aparece uma vez, com as duas fontes; discordância segue a ordem fixa; a origem mostra a fonte de cada campo.
  - Arquivos: `rastro/fontes/juncao.py`, `rastro/fluxo.py`, `tests/fontes/test_juncao.py`
  - Teste: `test_r04a_3_*` a `test_r04a_5_*`
  - Requisito: R04A.3–R04A.5
  - Revisão: @geison.santos

## Extensão: gravar a visita (branch `feat/gravar`, só se houver tempo)

O auditor grava o HAR pelo próprio Rastro, sem DevTools: abre um navegador, navega (à mão ou com um robô com travas) e a análise roda ao fechar. Base: os spikes de 13/11 (T58). Corre na branch `feat/gravar` e volta ao `main` por merge, sem rebase. Prazo limite: 08/12. O que não fechar fica nos planos futuros. T58 a T61 já entregam a gravação manual; T62 e T63 são o robô.

Sem revisor definido: os commits saem sem `Co-authored-by` até o grupo escolher quem revisa.

- [x] **T58 Registrar os spikes da gravação com Playwright**
  - Entrega: `docs/spike/gravacao-com-playwright.md` com o que os dois spikes de 13/11 mostraram.
  - Aceite: o documento traz como foi feito, os números contra o gabarito (Juice Shop, WebGoat, Drupal), o formato do HAR do Playwright (`mode: "minimal"`, sem `log.pages`, cookies só nos cabeçalhos), o tamanho do download, o Ctrl+C que perdia o HAR e o que fica para conferir no Windows.
  - Arquivos: `docs/spike/gravacao-com-playwright.md`
  - Teste: não se aplica.
  - Requisito: base para R24
  - Revisão: a definir

- [x] **T59 Especificar a gravação da visita**
  - Entrega: R24 no `requirements.md`, seção nova no `design.md` e a decisão 12 (o Rastro abre um navegador que a pessoa controla, com Playwright opcional).
  - Aceite: R24 cobre o comando, as dependências que faltam, a pasta da gravação, o aviso sobre a sessão no HAR, a análise ao fim, o robô e suas travas; o `product.md` e o `tech.md` deixam de pôr o Playwright como fora do escopo e explicam a exceção à dependência zero e à regra de rede; o PRD e o pitch acompanham.
  - Arquivos: `.kiro/specs/rastro/requirements.md`, `.kiro/specs/rastro/design.md`, `.kiro/specs/rastro/dependencias.md`, `docs/decisoes/12-gravar-com-playwright.md`, `.kiro/steering/product.md`, `.kiro/steering/tech.md`, `.kiro/steering/structure.md`
  - Pendente: o PRD (`docs/prd.pdf`) e o pitch só existem em PDF, sem o fonte no repositório; ficam para quando o grupo decidir entregar a extensão.
  - Teste: não se aplica.
  - Requisito: R24
  - Revisão: a definir

- [x] **T60 Gravar a visita à mão com `rastro gravar`**
  - Entrega: o comando `rastro gravar <url>` abre o Chrome (ou o Edge) pelo Playwright, espera a pessoa fechar a janela, grava o HAR numa pasta nova e roda a análise com as mesmas opções do `analisar`.
  - Aceite: sem o Playwright, sai com 1 e diz o comando de instalação; sem Chrome nem Edge, diz o que instalar; nunca instala nada; o HAR vai para `~/Rastro/gravacoes/<site>/<AAAA-MM-DD_HH-MM-SS>/visita.har`, sem sobrescrever; o import do Playwright só acontece nesse comando.
  - Arquivos: `rastro/captura/` (`sessao.py`, `pasta.py`, `playwright.py`), `rastro/cli.py`, `tests/captura/`, `tests/test_cli.py`, `pyproject.toml`, `requirements-dev.txt`, `docs/spike/gravacao-com-playwright.md`
  - Teste: `test_r24_*`, com o Playwright trocado por dublê. A abertura real do navegador e o Ctrl+C foram conferidos à mão no Linux (Juice Shop); fechar a janela e o Windows ficam para a T42.
  - Requisito: R24.1–R24.7, R16.1, R17.1, R20.2
  - Revisão: a definir

- [x] **T61 Avisar sobre a sessão gravada no HAR**
  - Entrega: o terminal avisa que o HAR gravado pelo comando guarda a sessão (cabeçalhos `Cookie` e `Set-Cookie`), e a checagem de cookie sem dado deixa de mandar "exportar o HAR completo" quando o HAR veio do `gravar`.
  - Aceite: o aviso aparece ao fim do `gravar`, logo depois do caminho do arquivo; a mensagem das checagens C06–C08 muda só no HAR do `gravar` (o `analisar` continua igual).
  - Arquivos: `rastro/cli.py`, `rastro/fluxo.py`, `rastro/configuracao/checagens.py`, `tests/test_cli.py`, `tests/configuracao/test_checagens.py`, `.kiro/specs/rastro/requirements.md`, `.kiro/specs/rastro/design.md`
  - Teste: `test_r24_*`, `test_r06_7_*`
  - Requisito: R24.8, R24.9, R06.7
  - Revisão: a definir

- [ ] **T62 Navegar sozinho com travas**
  - Entrega: `rastro gravar <url> --robo` navega pelos links do próprio site, com limite de páginas, tempo e profundidade, no máximo 2 páginas por família de URL e sem seguir links de sair, excluir ou com `token=`.
  - Aceite: nunca visita a mesma URL duas vezes; para no primeiro limite atingido e diz qual; o progresso aparece no terminal; Ctrl+C ou fechar a janela param o robô e o HAR é gravado com o que já foi coletado (`handle_sigint=False`).
  - Arquivos: `rastro/captura/robo.py`, `tests/captura/test_robo.py`
  - Teste: `test_r24_*`, com a navegação trocada por dublê (sem rede).
  - Requisito: R24.10–R24.14
  - Revisão: a definir

- [ ] **T63 Combinar o robô com a navegação da pessoa**
  - Entrega: no `--robo`, a pessoa faz login antes e aperta Enter para o robô começar; ao fim, a janela fica aberta para ela visitar mais páginas antes de fechar.
  - Aceite: sem Enter, o robô não começa; depois do robô, a gravação só termina quando a janela é fechada.
  - Arquivos: `rastro/captura/`, testes
  - Teste: `test_r24_*`
  - Requisito: R24.10, R24.15
  - Revisão: a definir

- [ ] **T64 Ensinar a gravar a visita**
  - Entrega: README, README técnico e a tela "Como usar" com o `gravar`, nos comandos de Linux e de Windows.
  - Aceite: o passo a passo instala o Playwright e grava uma visita do zero nos dois sistemas; a tela "Como usar" mostra o `gravar` como alternativa ao DevTools.
  - Arquivos: `README.md`, `README-TECNICO.md`, `frontend/src/`, `rastro/relatorio/modelo.html`
  - Teste: verificação manual.
  - Requisito: R24, R20.1
  - Revisão: a definir
