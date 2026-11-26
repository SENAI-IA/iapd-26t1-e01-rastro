---
name: rastro-nova-regra
description: Passo a passo para acrescentar ao Rastro uma checagem de configuração, uma assinatura de biblioteca, uma fonte de dados de vulnerabilidades, um provedor de IA ou uma trava contra invenção. Diz onde mexer, qual teste escrever, a cobertura esperada e a verificação antes do commit. Use ao implementar ou estender qualquer um desses cinco pontos.
---

# Acrescentar uma regra ao Rastro

Cinco pontos de extensão, cada um com lugar fixo. O que cada arquivo faz está em [`structure.md`](../../steering/structure.md) ("Onde colocar algo novo"); as regras de código e de teste, em [`codigo-python.md`](../../steering/codigo-python.md). Aqui fica só onde mexer e qual teste escrever.

## Antes de qualquer caso

1. **Spec primeiro.** A regra precisa de um critério `Rxx.y` no `requirements.md` e de uma task no `tasks.md`. Sem critério, não há teste com ID: escreva o critério antes.
2. **Teste com o ID do critério no nome** (`test_r06_1_csp_ausente_falha`), sem rede e sem IA: dublês de `tests/dubles.py`, entradas pequenas e feitas à mão em `tests/dados/`. Pasta nova em `rastro/` e em `tests/` leva um `__init__.py` vazio.
3. Se a regra muda o que o fluxo devolve, ela aparece nos testes de `tests/test_fluxo_da_analise.py` (com `tests/dados/loja.har`) e nas contagens dos testes de `tests/relatorio/` e `tests/comandos/`.

## Checagem de configuração

| Onde mexer | O quê |
|---|---|
| `configuracao/regras_das_checagens.py` | a `RegraDeChecagem` (próximo ID livre, título, severidade, quem resolve); checagem de cookie também em `IDENTIFICADORES_DAS_CHECAGENS_DE_COOKIE` (R24.9) |
| `configuracao/falhas_nos_cabecalhos.py` ou `falhas_nos_cookies.py` | a função que diz se uma resposta ou um `Cookie` falha |
| `configuracao/checagens.py` | a função `checar_*`, que usa `checar_paginas_do_site` ou `checar_cookies_do_site` (`avaliacao_do_site.py`: já dão o "não verificada" e a evidência), no fim da tupla `CHECAGENS` |
| `acao/correcoes_das_checagens.py` | o que fazer e o impacto, em `CORRECOES_DAS_CHECAGENS`; sem a linha, o plano de ação quebra |
| `design.md`, seção 10 | a linha da tabela |

**Teste:** em `tests/configuracao/test_checagens.py`, um caso que falha, um que passa e um de outro host que não conta; a função em `TODAS_AS_CHECAGENS` ou `CHECAGENS_DE_COOKIE` e o ID em `test_r06_8_...`. A função que diz se falha, em `test_falhas_nos_cabecalhos.py` ou `test_falhas_nos_cookies.py`. A regra entra no caso parametrizado `test_r08_2_...` de `tests/acao/test_plano_de_acao.py`.

## Assinatura de biblioteca

| Onde mexer | O quê |
|---|---|
| `identificacao/assinaturas.py` | uma linha em `ASSINATURAS`: pacote npm, nome no arquivo e regex do comentário de versão. Separador, versão e abertura do comentário são comuns a todas as linhas: não repita |
| `design.md`, seção 6, e R02.4 | a linha da tabela e o nome |

O padrão vem de um arquivo de verdade (alvo da `avaliacao/` ou CDN), conferido no `.js` e no `.min.js` publicados; procure no mesmo arquivo menções a outras bibliotecas que outra linha pegaria (o Lodash cita `Underscore.js 1.8.3`). As regras do padrão estão no `design.md`, seção 6.

**Teste:** em `tests/identificacao/test_assinaturas.py`: o caso parametrizado `test_r02_4_*`, pela URL (`test_r02_1_*`) sem confundir com nome que a contém, e pelo comentário (`test_r02_2_*`) sem confundir com menção em outro comentário. O teste contra o `avaliacao/gabarito.json` continua passando.

## Fonte de dados de vulnerabilidades

| Onde mexer | O quê |
|---|---|
| `fontes/<nome>.py` | classe que implementa `ConectorDeAvisos` (`fontes/conector.py`); a chamada com `baixar_json` (`fontes/requisicao_http.py`), a leitura dos campos em funções puras e `marcar_origem(aviso, NOME_DA_FONTE)` (`fontes/modelos.py`) no fim. Falha vira `ConsultaNaoRealizada(motivo)`. Campo que a fonte não traz pronto fica `None`: não calcule |
| `fontes/faixas_do_<nome>.py` | só se a faixa vier em outro formato: converte para o do GitHub (`>= x, < y`), para a trava 6 não mudar |
| `fontes/juncao_dos_avisos.py` | o `NOME_DA_FONTE` em `ORDEM_DAS_FONTES`, na posição de R04A.4 |
| `fontes/consulta_dos_avisos.py` e `fluxo_da_analise.py` | fonte complementar: parâmetro opcional de `analisar`; a falha vira `FonteSemResposta` e uma limitação (`CONSEQUENCIA_DA_FONTE_SEM_RESPOSTA`, em `relatorio/limitacoes_da_analise.py`) |
| `tests/dubles.py` e `tests/comandos/conftest.py` | o dublê (como `OsvFalso`) e a troca na fixture `fontes_falsas`, senão os testes dos comandos tentam a rede |
| `design.md`, seção 7; `tech.md`, "Rede"; `docs/decisoes/` | o endereço e o mapa dos campos; o nome da fonte; a decisão (nova, ou a 02 se só mudar a ordem) |

Fonte que só completa um campo, como o NVD, não usa `ConectorDeAvisos`: fica atrás de um protocolo pequeno, como `BuscaDeCvss` em `fontes/completar_cvss.py` ([decisão 10](../../../docs/decisoes/10-interface-do-nvd.md)).

**Teste:** em `tests/fontes/test_<nome>.py`, troque `urlopen` de `rastro.fontes.requisicao_http` por um dublê que guarda a `Request` e devolve uma resposta gravada em `tests/dados/<fonte>-*.json`. Cubra URL e cabeçalhos enviados, campos (inclusive ausentes), falha de rede, códigos HTTP de erro e aviso retirado.

## Provedor de IA

| Onde mexer | O quê |
|---|---|
| `ia/provedores/<nome>.py` | classe que cumpre `ProvedorDeIA` (`ia/provedor.py`); recebe o executável no construtor e roda a CLI com `executar_cli_da_ia` (`ia/provedores/execucao_da_cli.py`), prompt pela entrada padrão; tokens com `somar_tokens` (`contagem_de_tokens.py`) ou `None`; toda falha vira `FalhaDoProvedor` |
| `ia/escolha_da_ia.py` | nome e executável em `EXECUTAVEIS_DAS_IAS` |
| `comandos/comando_analisar.py` | nome e classe em `PROVEDORES_DAS_IAS` (`test_r14_1_cada_ia_tem_o_seu_provedor` falha se as duas tabelas divergirem) |
| `comandos/argumentos.py` | o nome no texto `AJUDA_IA` |
| `design.md`, seção 11 | a linha da tabela de provedores, com o comando conferido antes, como no spike T02 (`docs/historico/spike/clis-de-ia.md`) |

**Teste:** em `tests/ia/provedores/test_<nome>.py`, troque `subprocess.run` em `rastro.ia.provedores.execucao_da_cli`. Cubra a resposta lida, o prompt na entrada padrão (nunca nos argumentos), os tokens (e `None`), código de saída diferente de zero, tempo limite, resposta com erro ou vazia e `OSError`. Resposta gravada em `tests/dados/<nome>-resposta.*`. O nome entra nos casos parametrizados de `tests/ia/test_escolha_da_ia.py`. Cobertura: conta no total, mas não é meta.

## Trava contra invenção

| Onde mexer | O quê |
|---|---|
| `travas/<nome>.py` | a função que responde uma pergunta só e devolve o que passou e as `TravaAcionada` (`travas/modelos.py`). O que mais de uma trava usa fica num apoio em `travas/` (`json_estrito.py`, `marcacao_a_confirmar.py`, `versao_no_trecho.py`) |
| quem chama | trava sobre biblioteca: `travas/conferencia_das_bibliotecas.py` (com `mandar_para_a_confirmar`); trava que precisa dos trechos enviados: `identificacao/bibliotecas_pela_ia.py`; trava sobre aviso, explicação ou resposta inteira: o fluxo ou quem lê a resposta |
| `fontes/registro_npm.py` | só se a trava consulta o npm: a leitura fica atrás de `RegistroDePacotes`, e a trava recebe o registro como parâmetro |
| `frontend/src/zonas/detalhes/ComoConfirmarATrava.tsx` | trava que manda para "a confirmar": uma entrada em `COMO_CONFIRMAR_PELA_TRAVA`, com o mesmo nome de trava do Python; sem ela, o relatório mostra um texto genérico |
| `design.md`, seção 8, e R21 | a linha da tabela de travas (com o arquivo) e o critério |

Dado que a trava não consegue ler também barra, com o motivo: o que não foi conferido não passa. Os fatos do relatório vêm só das fontes e da fórmula (R21.8).

**Teste:** em `tests/travas/test_<nome>.py`, pelo menos um caso em que a IA (dublê) inventa algo e a trava barra, e um em que o dado verdadeiro passa. Se a trava consulta o npm, use o `RegistroFalso`.

## Verificação e commit

Rode a [verificação](../../../README-TECNICO.md#verificação). Passou quando `ruff` e `mypy` não acusam nada, o `pytest` termina sem falhas e a pasta da regra fica acima de 80% de cobertura (menos os provedores de IA).

Depois, um commit só para a task, como no [`processo.md`](../../steering/processo.md). Se o padrão de construção mudou, o steering e esta skill mudam no mesmo commit.
