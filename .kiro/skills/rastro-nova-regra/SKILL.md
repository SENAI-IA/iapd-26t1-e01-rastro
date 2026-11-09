---
name: rastro-nova-regra
description: Passo a passo para acrescentar ao Rastro uma checagem de configuração, uma assinatura de biblioteca, uma fonte de dados de vulnerabilidades, um provedor de IA ou uma trava contra invenção. Diz onde fica o arquivo, qual teste escrever, a cobertura esperada e a verificação antes do commit. Use ao implementar ou estender qualquer um desses cinco pontos.
---

# Acrescentar uma regra ao Rastro

Cinco pontos de extensão, cada um com lugar fixo (`.kiro/steering/structure.md`, "Onde colocar algo novo"). Escolha o caso, siga os passos e termine na verificação.

## Antes de qualquer caso

1. **Spec primeiro.** A regra nova precisa de um critério `Rxx.y` em `.kiro/specs/rastro-mvp/requirements.md` e de uma task no `tasks.md`. Sem critério, não há teste com ID, então pare e escreva o critério.
2. **Pasta que ainda não existe:** crie seguindo `structure.md` e o `design.md` (seção 2), com o `tests/` espelhando o `rastro/`. Cada pasta nova, em `rastro/` e em `tests/`, leva um `__init__.py` vazio, porque os nomes de arquivo se repetem (`identificacao/test_ia.py`, `explicacao/test_ia.py`).
3. **Nome do teste** leva o critério e descreve o comportamento: `test_r06_1_csp_ausente_falha`. Cada critério tem pelo menos um teste.
4. **Nada de rede nem de IA nos testes.** O `tests/conftest.py` bloqueia a rede. Fonte, registro do npm e IA viram dublês (`ConectorFalso`, `ProvedorFalso`, `urlopen` ou `subprocess.run` trocados com `monkeypatch`). `ConectorFalso`, `RegistroFalso` e `ProvedorFalso` (respostas e falhas em fila, prompts recebidos guardados) de uso geral ficam em `tests/dubles.py`, com o HAR de ponta a ponta `tests/dados/loja.har`; a regra nova deve aparecer nos testes de `tests/test_fluxo.py` quando mudar o que o fluxo devolve. Arquivo de entrada de teste (HAR, resposta gravada) fica em `tests/dados/`, feito à mão, pequeno e sem dado real.
5. **Regra de negócio é função pura:** sem arquivo, rede, IA ou relógio dentro dela. Nomes em português, tipos em tudo, sem comentário: condição composta vira função com nome.

## Checagem de configuração

1. **Arquivo:** uma função pura nova em `rastro/configuracao/checagens.py`, assinatura `(requisicoes, site) -> Checagem`, com o próximo ID livre (`C09`…). Acrescente a função no fim da tupla `CHECAGENS`, no mesmo arquivo: é por ela que o fluxo (`checar_configuracao`) roda as checagens. Fora da tupla, a checagem nunca chega ao relatório.
2. **Dados fixos da regra:** uma `RegraDeChecagem` (ID, título, severidade, quem resolve) no topo de `checagens.py`, como na tabela do `design.md` (seção 10). Acrescente a linha nessa tabela.
3. **Só o site analisado:** ignore respostas de outros hosts. Cabeçalho falha se alguma resposta HTML do site falha, e a evidência é a primeira delas. Use `paginas_html_do_site` e `checar_paginas_do_site`, que já dão o "não verificada" quando não há página HTML do site e a evidência do "passou"; a checagem nova só escreve a função que diz se uma página falha. Regra que não se aplica ao site (ex.: HSTS sem HTTPS) fica "não verificada", nunca "passou".
   Checagem de cookie olha as respostas do site com cookie, de qualquer tipo: use `respostas_do_site_com_cookies` e `checar_cookies_do_site`, que dão o "não verificada" do HAR sem cookies (R06.7) e listam só o nome do cookie, nunca o valor; a checagem nova só escreve a função que diz se um `Cookie` falha.
4. **Plano de ação:** acrescente em `CORRECOES_DAS_CHECAGENS`, em `rastro/acao/plano.py`, o que fazer e o impacto da checagem (texto fixo, sem IA), e a regra nova no caso parametrizado `test_r08_2_toda_checagem_tem_o_que_fazer_e_impacto`, em `tests/acao/test_plano.py`. Sem essa linha, a checagem com falha quebra a montagem do plano.
5. **Teste** em `tests/configuracao/test_checagens.py`: um caso que falha, um que passa e um com resposta de outro host que não conta. Monte as `Requisicao` no próprio teste, sem HAR. Acrescente a função na lista `TODAS_AS_CHECAGENS` ou `CHECAGENS_DE_COOKIE` do teste e o ID novo em `test_r06_8_checar_configuracao_roda_todas_as_regras_na_ordem_dos_ids`; os testes de `tests/relatorio/test_json.py` e `tests/test_cli.py` contam as ações e checagens do `loja.har` e mudam se a regra nova falhar nele.
6. **Cobertura:** acima de 80% em `configuracao/`.

## Assinatura de biblioteca

1. **Arquivo:** uma linha nova em `ASSINATURAS`, em `rastro/identificacao/assinaturas.py`: pacote npm, nome no arquivo (ex.: `jquery-ui`) e regex do comentário de versão. É dado, não função nova. O separador e a versão do nome do arquivo são comuns a todas as linhas (`design.md`, seção 6): não repita na linha.
2. **Base real:** o padrão vem de um arquivo de verdade (alvo da `avaliacao/` ou CDN), nunca de memória. Acrescente a linha na tabela do `design.md` (seção 6) e o nome em R02.4.
3. **Regras do padrão:** o nome do arquivo é o caminho com os parâmetros, sem o host, e só de scripts; o `?v=` e o `?ver=` já valem para toda linha pelo separador comum; a coluna do comentário é o texto logo depois da abertura (`/*`, `/**`, `/*!`, `//`, `//!` ou ` * ` no começo da linha), que é comum a todas as linhas: não repita a abertura na linha; nome e comentário divergentes, vale o comentário; bibliotecas iguais se juntam por `(pacote, versao)` sozinhas, em `identificar_por_assinatura`. Confira o padrão no arquivo `.js` e no `.min.js` publicados (o minificado às vezes tira o comentário ou muda a abertura) e procure, no mesmo arquivo, menções a outras bibliotecas que o padrão de outra linha pegaria (ex.: o Lodash cita `Underscore.js 1.8.3`).
4. **Teste** em `tests/identificacao/test_assinaturas.py`: a biblioteca entra no caso parametrizado `test_r02_4_*` e no conjunto da tabela; reconhece pela URL (`test_r02_1_*`) e não confunde com outro nome que a contém (ex.: `jquery-ui-1.10.4.js` não é jQuery, `react-bootstrap@1.0.0` não é Bootstrap); reconhece pelo comentário (`test_r02_2_*`) e não confunde com menção dentro de outro comentário (ex.: `Requires jQuery v1.7.2`). Monte as `Requisicao` no próprio teste, com URL e conteúdo, sem HAR. O teste que compara com o `avaliacao/gabarito.json` (os três HARs reais) deve continuar passando: biblioteca nova não pode aparecer onde o gabarito não espera.
5. **Cobertura:** acima de 80% em `identificacao/`.

## Fonte de dados de vulnerabilidades

1. **Arquivo:** `rastro/fontes/<nome>.py`, uma classe que implementa `ConectorDeAvisos` (`rastro/fontes/conector.py`): `consultar(pacote, versao) -> list[Aviso]`. Fonte que só completa um campo, sem buscar avisos (como o NVD), não usa a interface.
2. **Só fonte oficial** (R04.5), com `urllib.request` e tempo limite. Erro de rede, tempo esgotado, limite, 5xx ou resposta fora do formato vira `ConsultaNaoRealizada(motivo)` (de `conector.py`), com o motivo pronto em português; o fluxo marca a biblioteca "não consultada" e a análise segue (R04.3). A leitura dos campos fica em funções puras no mesmo arquivo (`converter_resposta`), separadas da chamada à rede. Faixa de versão: um `Aviso` por faixa do pacote; quem escolhe é a trava 6.
3. **Junção:** avisos iguais de fontes diferentes se juntam em `fontes/juncao.py`, pela ordem fixa de fontes (R04A.4). A faixa de versão passa pela trava 6.
4. **Teste** em `tests/fontes/test_<nome>.py`: troque `urlopen` (importado no módulo da fonte com `from urllib.request import urlopen`) por um dublê que guarda a `Request` e devolve uma resposta gravada em `tests/dados/<fonte>-*.json`. Cubra a URL e os cabeçalhos enviados, a conversão dos campos (inclusive os ausentes), a falha de rede, os códigos HTTP de erro e o aviso retirado. Variável de ambiente (token) com `monkeypatch.setenv`/`delenv`.
5. **Cobertura:** acima de 80% em `fontes/`.
6. **Steering:** acrescente o domínio na seção "Rede" do `tech.md` e registre a decisão em `docs/decisoes/`.

## Provedor de IA

1. **Arquivo:** `rastro/ia/provedores/<nome>.py`, uma classe que cumpre `ProvedorDeIA` (`nome` e `executar(prompt) -> RespostaDoProvedor`). Só o `ia/cliente.py` chama o provedor.
2. **Como chamar a CLI:** o provedor recebe no construtor o caminho do executável que `localizar_cli` (`ia/cliente.py`) achou com `shutil.which`; `subprocess.run(..., input=prompt, capture_output=True, encoding="utf-8", timeout=120)`, prompt pela entrada padrão, nunca como argumento (R14.4). Opções que desligam ferramentas e gravação. Tokens quando a CLI informar; senão, `None`. Toda falha (código de saída, tempo limite, erro na resposta) vira `FalhaDoProvedor(motivo)`, de `rastro/ia/cliente.py`: o `ClienteDeIA` registra a chamada como falha e a análise segue.
3. **Escolha:** acrescente o nome e o executável em `EXECUTAVEIS_DAS_IAS`, em `rastro/ia/cliente.py`: é por essa tabela que `--ia` e `RASTRO_IA` são validados (R14.1, R14.2) e a CLI é procurada (R14.3). Ligue o nome à classe em `PROVEDORES_DAS_IAS`, no `cli.py` (é ali que o cliente é montado com o provedor; `test_r14_cada_ia_tem_o_seu_provedor` falha se as duas tabelas divergirem). Acrescente o nome também no texto `AJUDA_IA` do `cli.py` e nos casos parametrizados de `tests/ia/test_cliente.py` e a linha na tabela de provedores do `design.md` (seção 11). Comando conferido antes, como no spike T02 (`docs/spike/clis-de-ia.md`).
4. **Teste** em `tests/ia/provedores/test_<nome>.py`: troque `subprocess.run` com `monkeypatch` (no módulo do provedor). Cubra a resposta lida, o prompt indo pela entrada padrão (e nunca nos argumentos), os tokens (e `None` quando faltarem), o código de saída diferente de zero, o tempo limite, a resposta com erro ou sem texto e a CLI que sumiu depois de localizada (`OSError`). A CLI ausente antes da análise (R14.3) já é testada em `tests/ia/test_cliente.py`. Resposta gravada da CLI fica em `tests/dados/<nome>-resposta.json` (`.jsonl` quando a CLI solta um evento JSON por linha, como o Codex), tirada do spike ou de uma chamada real numa pasta vazia (`.txt` quando a CLI responde em texto puro, como o Kiro). Se a CLI devolve eventos, cubra também mais de um evento de resposta e linha que não é JSON.
5. **Cobertura:** o provedor conta no total, mas não é meta.

## Trava contra invenção

1. **Arquivo:** `rastro/travas/<nome>.py`, uma função pura que responde a uma pergunta só (ex.: "a versão aparece no trecho?"). Trava sobre biblioteca é chamada em `rastro/travas/conferencia.py`, que decide "confirmada" ou "a confirmar" (biblioteca que já chega "a confirmar" não é conferida de novo). Exceção: trava que precisa dos trechos enviados à IA (2 e 3, `conferir_ancoragem`) é chamada em `rastro/identificacao/ia.py`, logo depois do formato. Trava sobre aviso, explicação ou resposta inteira da IA é chamada direto no fluxo e devolve o que passou e as `TravaAcionada` (ex.: `descartar_fora_da_faixa` em `faixa_de_versao.py`, `conferir_formato` em `formato.py`).
   Trava sobre biblioteca devolve `(biblioteca, travas_acionadas)`: barrada, sai com `situacao="a_confirmar"` e o nome da trava em `travas_que_falharam`, sem repetir (ex.: `conferir_ancoragem` em `ancoragem.py`). Se a task não lista o `conferencia.py`, a ligação fica para a task do fluxo.
   Trava que consulta o npm (4 e 5) não é função pura: a leitura fica em `rastro/fontes/registro_npm.py`, atrás de `RegistroDePacotes` (`existe` para a trava 4, `ler_codigo` para a 5), e a trava recebe o registro como parâmetro: a 4 está no próprio `conferencia.py`; a 5 em `codigo_publicado.py` (`conferir_codigo_publicado`), com a comparação em funções puras, e é chamada pelo `conferencia.py`. Tudo o que a leitura não consegue fazer (rede, limite de tamanho, integridade, pacote ilegível) vira `ConsultaNaoRealizada` com o motivo, e a trava barra com esse motivo. Sem resposta do registro (`ConsultaNaoRealizada`), a biblioteca por assinatura segue com `conferida_no_npm=None` e a da IA vai para "a confirmar" (R21.9).
2. **O que barra fica registrado** como `TravaAcionada` (trava, alvo, motivo), de `rastro/travas/modelos.py`, no painel da IA (R21.10). Dado que a trava não consegue ler (faixa, versão) também barra, com o motivo: o que não foi conferido não passa. A IA nunca preenche CVE, versão, CVSS, EPSS, nota ou versão-alvo (R21.8).
3. **Spec:** acrescente a linha na tabela de travas do `design.md` (seção 8) e o critério em R21.
   Trava que manda biblioteca para "a confirmar": acrescente o "como confirmar à mão" no `comoConfirmar` de `frontend/src/componentes/ItemAConfirmar.tsx`, com o mesmo nome de trava do Python (`TRAVA_...`). Sem a linha, o relatório mostra um texto genérico.
4. **Teste** em `tests/travas/test_<nome>.py`: pelo menos um caso em que a IA (dublê) inventa algo e a trava barra, e um em que o dado verdadeiro passa. Se a trava consulta o npm, use o `RegistroDePacotes` dublê.
5. **Cobertura:** acima de 80% em `travas/`.

## Verificação antes do commit

Com o `.venv` ativo, na raiz (seção "Verificação" do README):

```
ruff check
mypy rastro
pytest --cov=rastro --cov-report=term
```

Passou quando o `ruff` mostra `All checks passed!`, o `mypy` mostra `Success`, o `pytest` termina sem falhas e a pasta da regra fica acima de 80%.

Depois, um commit só para a task, direto no `main` (`.kiro/steering/processo.md`): `feat(<escopo>): <o que muda> (Tnn)`, com o `[x]` no `tasks.md`, o cartão em "Em revisão" no `kanban.md` e a linha `Co-authored-by` do revisor. Se o padrão de construção mudou, atualize o `.kiro/steering/` e esta skill no mesmo commit.
