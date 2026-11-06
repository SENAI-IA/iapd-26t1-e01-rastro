# Estrutura

## Princípios

- **Clareza e qualidade, sem over engineering.** Só existe abstração que resolve um problema de hoje. Na dúvida, a solução simples.
- **Responsabilidade única (SRP) em pasta, arquivo e função.** Se a descrição precisa de "e", está fazendo coisas demais.
- **Núcleo puro, entrada e saída nas bordas.** Ler arquivo, chamar API, chamar IA e gravar relatório ficam nas bordas. Nota, prioridade, checagens e travas são funções puras.
- **Interface só onde há troca real:** a fonte de dados (`ConectorDeAvisos`), o registro do npm (`RegistroDePacotes`) e o cliente da IA (`ProvedorDeIA`, com três provedores reais). Nos testes, os três viram dublês. Nenhuma outra parte ganha interface.
- **A IA sugere, a regra confirma:** toda saída da IA passa por `travas/` antes de virar dado.
- **Um único ponto de chamada à IA**, que mede tempo e tokens.
- **Dados separados da apresentação.** O núcleo gera JSON; o React só exibe.
- **O código segue o fluxo da apresentação:** HAR → identificar → conferir → consultar → calcular → explicar → relatar, nessa ordem em `fluxo.py`.

## Pastas

```
rastro/
  cli.py                   lê os argumentos e chama o fluxo
  fluxo.py                 orquestra as etapas, sem regra própria
  har/                     leitor.py, modelos.py, site.py
  identificacao/           modelos.py, assinaturas.py, bundles.py, ia.py
  travas/                  formato.py, ancoragem.py, codigo_publicado.py, faixa_de_versao.py, explicacao.py, conferencia.py
  fontes/                  conector.py (interface), github_advisory.py, registro_npm.py; opcionais: osv.py, nvd.py, juncao.py
  risco/                   nota.py, prioridade.py
  configuracao/            checagens.py (uma função por checagem)
  explicacao/              ia.py
  acao/                    plano.py, task.py
  ia/
    cliente.py             interface única, escolha do provedor, medição
    sanitizacao.py         tira dados sensíveis do que vai para a IA
    provedores/            kiro.py, claude.py, codex.py
    prompts/               prompts versionados, com exemplo de entrada e saída
  relatorio/               json.py, html.py, gravacao.py, modelo.html (build do frontend, versionado)
tests/                     mesma estrutura de rastro/
frontend/                  React (ver frontend-react.md)
docs/
  decisoes/                um arquivo por decisão importante
  cobertura/               relatório de cobertura (Windows e Linux)
.kiro/                     specs (com tasks e kanban), steering, skills
```

Nada em `rastro/`, `frontend/`, `.kiro/` ou no README depende de arquivo fora do repositório.

## Onde colocar algo novo

- **Checagem nova:** uma função em `configuracao/checagens.py` e seu teste.
- **Fonte de dados nova:** um arquivo em `fontes/` que implementa `conector.py`.
- **IA nova:** um arquivo em `ia/provedores/`.
- **Assinatura nova:** em `identificacao/assinaturas.py`.
- **Trava nova:** um arquivo em `travas/`, chamado por `conferencia.py`, com teste em que a IA (dublê) inventa algo e a trava barra.

A skill `rastro-nova-regra` (`.kiro/skills/rastro-nova-regra/SKILL.md`) descreve o passo a passo.
