# Estrutura

## Princípios

- **Clareza e qualidade, sem over engineering.** Só existe abstração que resolve um problema de hoje. Na dúvida, a solução simples.
- **Responsabilidade única (SRP) em pasta, arquivo e função.** Se a descrição precisa de "e", está fazendo coisas demais.
- **Núcleo puro, entrada e saída nas bordas.** Ler arquivo, chamar API, chamar IA e gravar relatório ficam nas bordas. Nota, prioridade, checagens e travas são funções puras.
- **Interface só onde há troca real:** a fonte de dados (`ConectorDeAvisos`), o registro do npm (`RegistroDePacotes`), o provedor da IA (`ProvedorDeIA`, em `ia/provedor.py`, com três provedores reais), o CVSS do NVD (`BuscaDeCvss`, ver `docs/decisoes/10-interface-do-nvd.md`) e o navegador que grava a visita (`SessaoDeGravacao`, ver `docs/decisoes/12-gravar-com-playwright.md`). Nos testes, os cinco viram dublês. Nenhuma outra parte ganha interface.
- **A IA sugere, a regra confirma:** toda saída da IA passa por `travas/` antes de virar dado.
- **Um único ponto de chamada à IA**, que mede tempo e tokens.
- **Dados separados da apresentação.** O núcleo gera JSON; o React só exibe.
- **O código segue o fluxo da apresentação:** HAR → identificar → conferir → consultar → calcular → explicar → relatar, nessa ordem em `fluxo_da_analise.py`.
- **Pentest ativo isolado:** `pentest/` tem fluxo próprio para `pentest --autorizo`; o resultado nunca entra na nota nem no plano (`docs/decisoes/13-pentest-por-comando-separado.md`).

## Pastas

```
rastro/
  cli.py                   entrada do comando rastro: lê os argumentos e despacha para o comando escolhido
  comandos/                um arquivo por comando da linha de comando: comando_analisar.py, comando_gravar.py,
                           comando_pentest.py, comando_como_usar.py, comando_instalar.py, comando_desinstalar.py;
                           e as peças que eles dividem: argumentos.py, resumo_no_terminal.py, navegador.py, saida_de_erro.py
  atalho.py                cria e remove o comando rastro na pasta do usuário (instalar e desinstalar)
  fluxo_da_analise.py      orquestra as etapas, sem regra própria
  modelos_da_analise.py    a Analise: o resultado completo que o fluxo entrega ao relatório
  versao_semver.py         lê e compara versões e faixas semver (usado por travas/, fontes/ e acao/)
  gravacao_segura.py       grava sem sobrescrever: pasta nova, arquivo novo e nome de pasta seguro no Windows
  andamento.py             interface que o fluxo usa para avisar a etapa e os itens
  terminal.py              linha ao vivo e andamento da análise no terminal
  har/                     leitor_do_har.py, modelos.py, site.py, visita.py
  identificacao/           modelos.py, assinaturas.py, trechos_dos_bundles.py, bibliotecas_pela_ia.py
  travas/                  formato_das_bibliotecas.py, ancoragem.py, codigo_publicado.py, faixa_de_versao.py,
                           explicacao_sem_fato_novo.py, conferencia_das_bibliotecas.py
  fontes/                  modelos.py (Aviso, FonteSemResposta, AvisosDaBiblioteca, marcar_origem), conector.py (interface e ConsultaNaoRealizada),
                           requisicao_http.py (baixa o JSON e monta os motivos de falha, comum a todas as fontes),
                           filtro_do_pacote_npm.py, github_advisory.py, consulta_dos_avisos.py,
                           registro_npm.py (HTTP do registro) e pacote_npm.py (integridade e leitura do tar em memória);
                           opcionais: osv.py, faixas_do_osv.py, nvd.py (cliente), completar_cvss.py (BuscaDeCvss), juncao_dos_avisos.py
  risco/                   modelos.py, nota.py, prioridade.py, achados.py
  configuracao/            checagens.py (uma função por checagem)
  explicacao/              modelos.py, explicacao_dos_achados.py
  acao/                    modelos.py, plano_de_acao.py, texto_da_tarefa.py
  ia/
    provedor.py            contrato do provedor (ProvedorDeIA, RespostaDoProvedor, FalhaDoProvedor)
    cliente.py             interface única: pergunta ao provedor e mede tempo e tokens (ChamadaDaIA)
    escolha_da_ia.py       escolhe e valida a IA (--ia, RASTRO_IA) e localiza a CLI
    montagem_do_prompt.py  lê o prompt de prompts/ e põe a entrada no marcador {{entrada}}
    sanitizacao.py         tira dados sensíveis do que vai para a IA
    provedores/            kiro.py, claude.py, codex.py; execucao_da_cli.py (roda a CLI, comum aos três),
                           contagem_de_tokens.py (soma os tokens informados, comum a claude e codex)
    prompts/               prompts versionados, com exemplo de entrada e saída
  relatorio/               montagem_do_relatorio.py (esqueleto do JSON), limitacoes_da_analise.py, resumo_do_relatorio.py,
                           painel_da_ia.py, visita_no_relatorio.py, pagina_do_relatorio.py, gravacao_do_relatorio.py,
                           modelo.html (build do frontend, versionado)
  captura/                 sessao.py (interface), navegador_playwright.py (único import do Playwright), pasta.py, robo.py
  pentest/                 pentest --autorizo, isolado da análise: modelos.py (com as constantes do formato), erros.py,
                           privacidade.py, sonda.py, alvos_da_sonda.py (quais requisições do HAR são sondadas),
                           regras_dos_cabecalhos.py (leitura pura dos cabeçalhos), validacoes.py (uma função por validação),
                           resumo_do_pentest.py, conferencia_do_resultado.py, leitura_do_resultado.py,
                           gravacao_do_resultado.py, execucao_do_pentest.py
tests/                     mesma estrutura de rastro/
frontend/                  React (ver frontend-react.md)
docs/
  decisoes/                um arquivo por decisão importante
  cobertura/               resultado da verificação (linux.md, windows.md) e html/ (relatório do pytest-cov)
  prints/                  telas do relatório usadas no README
.kiro/                     specs (com tasks e kanban), steering, skills
```

Nada em `rastro/`, `frontend/`, `.kiro/` ou no README depende de arquivo fora do repositório.

## Onde colocar algo novo

- **Direção das dependências:** uma camada só importa das que vêm antes dela no fluxo (har → identificacao → travas → fontes → risco → explicacao → configuracao → acao → relatorio). A exceção é `travas/`, que usa as interfaces e os modelos de `fontes/` (`Aviso`, `RegistroDePacotes`, `AvisosDaBiblioteca`), porque a trava do npm consulta o registro e a trava da faixa roda depois da consulta. O que várias camadas usam fica num módulo neutro na raiz de `rastro/` (`versao_semver.py`, `gravacao_segura.py`, `modelos_da_analise.py`) ou no modelo de quem vem antes (ex.: `nome_com_versao` em `identificacao/modelos.py`, `agrupar_por_biblioteca` e `achados_da_biblioteca` em `risco/achados.py`, rótulo e ordem da prioridade em `risco/prioridade.py`).
- **Checagem nova:** uma função em `configuracao/checagens.py` (e na tupla `CHECAGENS`) e seu teste, e o que fazer e o impacto dela em `acao/plano_de_acao.py`.
- **Fonte de dados nova:** um arquivo em `fontes/` que implementa `conector.py`.
- **IA nova:** um arquivo em `ia/provedores/` (que roda a CLI com `execucao_da_cli.py`) e o nome em `EXECUTAVEIS_DAS_IAS` (`ia/escolha_da_ia.py`).
- **Assinatura nova:** em `identificacao/assinaturas.py`.
- **Trava nova:** um arquivo em `travas/`, chamado por `conferencia_das_bibliotecas.py` (trava sobre biblioteca) ou direto pelo fluxo (trava sobre aviso ou explicação), com teste em que a IA (dublê) inventa algo e a trava barra.

- **Regra nova no pentest:** uma função `validar_*` em `pentest/validacoes.py` (chamada por `validar_cabecalhos`), com a leitura do cabeçalho em `pentest/regras_dos_cabecalhos.py`, ou uma regra de escolha de alvo em `pentest/alvos_da_sonda.py`, com teste que prova o limite de segurança. O fluxo da análise não muda.

A skill `rastro-nova-regra` (`.kiro/skills/rastro-nova-regra/SKILL.md`) descreve o passo a passo.
