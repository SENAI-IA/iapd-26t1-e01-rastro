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
4. **Nada de rede nem de IA nos testes.** O `tests/conftest.py` bloqueia a rede. Fonte, registro do npm e IA viram dublês (`ConectorFalso`, `ProvedorFalso`, `urlopen` ou `subprocess.run` trocados com `monkeypatch`). Arquivo de entrada de teste (HAR, resposta gravada) fica em `tests/dados/`, feito à mão, pequeno e sem dado real.
5. **Regra de negócio é função pura:** sem arquivo, rede, IA ou relógio dentro dela. Nomes em português, tipos em tudo, sem comentário: condição composta vira função com nome.

## Checagem de configuração

1. **Arquivo:** uma função pura nova em `rastro/configuracao/checagens.py`, assinatura `(requisicoes, site) -> Checagem`, com o próximo ID livre (`C09`…).
2. **Dados fixos da regra:** severidade e quem resolve, como na tabela do `design.md` (seção 10). Acrescente a linha nessa tabela.
3. **Só o site analisado:** ignore respostas de outros hosts. Cabeçalho falha se alguma resposta HTML do site falha, e a evidência é a primeira delas.
4. **Teste** em `tests/configuracao/test_checagens.py`: um caso que falha, um que passa e um com resposta de outro host que não conta. Monte as `Requisicao` no próprio teste, sem HAR.
5. **Cobertura:** acima de 80% em `configuracao/`.

## Assinatura de biblioteca

1. **Arquivo:** uma linha nova em `ASSINATURAS`, em `rastro/identificacao/assinaturas.py`: pacote npm, nome no arquivo (ex.: `jquery-ui`) e regex do comentário de versão. É dado, não função nova. O separador e a versão do nome do arquivo são comuns a todas as linhas (`design.md`, seção 6): não repita na linha.
2. **Base real:** o padrão vem de um arquivo de verdade (alvo da `avaliacao/` ou CDN), nunca de memória. Acrescente a linha na tabela do `design.md` (seção 6) e o nome em R02.4.
3. **Regras do padrão:** o nome do arquivo é o caminho com os parâmetros, sem o host, e só de scripts; o `?v=` e o `?ver=` já valem para toda linha pelo separador comum; o comentário começa no início de um comentário (`/*`, `/*!`, `//`, `//!`, ` * `); nome e comentário divergentes, vale o comentário.
4. **Teste** em `tests/identificacao/test_assinaturas.py`: a biblioteca entra no caso parametrizado `test_r02_4_*` e no conjunto da tabela; reconhece pela URL (`test_r02_1_*`) e não confunde com outro nome que a contém (ex.: `jquery-ui-1.10.4.js` não é jQuery, `react-bootstrap@1.0.0` não é Bootstrap); reconhece pelo comentário (`test_r02_2_*`) e não confunde com menção dentro de outro comentário (ex.: `Requires jQuery v1.7.2`). Monte as `Requisicao` no próprio teste, com URL e conteúdo, sem HAR.
5. **Cobertura:** acima de 80% em `identificacao/`.

## Fonte de dados de vulnerabilidades

1. **Arquivo:** `rastro/fontes/<nome>.py`, uma classe que implementa `ConectorDeAvisos` (`rastro/fontes/conector.py`): `consultar(pacote, versao) -> list[Aviso]`. Fonte que só completa um campo, sem buscar avisos (como o NVD), não usa a interface.
2. **Só fonte oficial** (R04.5), com `urllib.request` e tempo limite. Erro de rede, limite ou 5xx vira "não consultada" com o motivo, e a análise segue (R04.3).
3. **Junção:** avisos iguais de fontes diferentes se juntam em `fontes/juncao.py`, pela ordem fixa de fontes (R04A.4). A faixa de versão passa pela trava 6.
4. **Teste** em `tests/fontes/test_<nome>.py`: troque `urlopen` por uma função que devolve uma resposta gravada em `tests/dados/`. Cubra a conversão dos campos, a falha de rede e o aviso retirado.
5. **Cobertura:** acima de 80% em `fontes/`.
6. **Steering:** acrescente o domínio na seção "Rede" do `tech.md` e registre a decisão em `docs/decisoes/`.

## Provedor de IA

1. **Arquivo:** `rastro/ia/provedores/<nome>.py`, uma classe que cumpre `ProvedorDeIA` (`nome` e `executar(prompt) -> RespostaDoProvedor`). Só o `ia/cliente.py` chama o provedor.
2. **Como chamar a CLI:** executável por `shutil.which`, `subprocess.run(..., input=prompt, capture_output=True, encoding="utf-8", timeout=120)`, prompt pela entrada padrão, nunca como argumento (R14.4). Opções que desligam ferramentas e gravação. Tokens quando a CLI informar; senão, `None`.
3. **Escolha:** acrescente o nome às opções de `--ia` e `RASTRO_IA` (R14.1, R14.2) e a linha na tabela de provedores do `design.md` (seção 11). Comando conferido antes, como no spike T02 (`docs/spike/clis-de-ia.md`).
4. **Teste** em `tests/ia/provedores/test_<nome>.py`: troque `shutil.which` e `subprocess.run` com `monkeypatch`. Cubra a resposta lida, o prompt indo pela entrada padrão, o código de saída diferente de zero, o tempo limite e a CLI ausente (R14.3).
5. **Cobertura:** o provedor conta no total, mas não é meta.

## Trava contra invenção

1. **Arquivo:** `rastro/travas/<nome>.py`, uma função pura que responde a uma pergunta só (ex.: "a versão aparece no trecho?"). Chame-a em `rastro/travas/conferencia.py`, que decide "confirmada" ou "a confirmar".
2. **O que barra fica registrado** como `TravaAcionada` (trava, alvo, motivo) no painel da IA (R21.10). A IA nunca preenche CVE, versão, CVSS, EPSS, nota ou versão-alvo (R21.8).
3. **Spec:** acrescente a linha na tabela de travas do `design.md` (seção 8) e o critério em R21.
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
