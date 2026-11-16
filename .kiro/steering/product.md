# Produto

**Rastro** lê a navegação gravada de um site (arquivo HAR) e diz quais bibliotecas com falhas conhecidas ele usa e o que corrigir primeiro.

## Para quem

- **Auditor:** roda a análise sob demanda, quando decide auditar um sistema. Não é especialista em segurança.
- **Dev:** recebe a task e corrige.
- **PO:** acompanha o risco e as correções.

Tudo precisa ser compreensível para quem não é de segurança.

## Como funciona

1. **Grave:** HAR exportado no DevTools ou, opcional, gravado pelo próprio Rastro (`rastro gravar`, com Playwright).
2. **Identifique:** bibliotecas e versões por assinatura; em bundles, a IA reconhece pelo código.
3. **Confira:** travas fixas conferem tudo o que a IA sugeriu.
4. **Consulte:** GitHub Advisory (CVE, CVSS, EPSS); OSV e NVD se houver tempo.
5. **Priorize:** `nota = 10 × (0,5 × CVSS/10 + 0,5 × percentil EPSS)`. Alta ≥ 7,5; média ≥ 6,5.
6. **Aja:** plano de ação explicado pela IA, com teste de verificação e task pronta.

## Escopo

Entra: CLI, relatório JSON e HTML, GitHub Advisory, OSV e NVD, bibliotecas front-end, cabeçalhos e cookies, travas contra invenção, modo foco, replay da visita, tour guiado e guia "Como usar", só análise passiva. Requisitos R01 a R23 da spec (`.kiro/specs/rastro/requirements.md`). Extensão na branch `feat/gravar`, se der tempo: gravar a visita (R24), à mão ou com um robô que só segue links.

Fica fora: scan ativo, código-fonte, integração com Azure DevOps ou GitLab, outras fontes (KEV, Exploit-DB, Vulners), base de falsos positivos, execução na esteira (CI) e Docker. Planos futuros no fim do `requirements.md`.

**Na dúvida, fica fora.** O Rastro precisa estar 100% funcional em 10/12/2026.

## Papel da IA

- **Faz:** reconhece bibliotecas em bundles, explica achados em linguagem simples, sugere teste de verificação, dá contexto.
- **Não faz:** calcula a nota, esconde achados, pesquisa na internet, recebe cookies, senhas ou tokens.
- **A IA sugere, a regra confirma.** Toda saída da IA passa pelas travas antes de virar dado. O que não passa fica "a confirmar", fora da nota.
- Nunca preenche CVE, versão, CVSS, EPSS, nota ou versão-alvo: isso vem só das fontes e da fórmula.
- O relatório mostra o que a IA fez: chamadas, o que recebeu e devolveu, tokens, tempo e o que cada trava barrou.
- Sem IA (`--sem-ia`) a análise roda, mas o terminal e o relatório avisam que ela é incompleta.

## Princípios de UX

- **Primeiro entender, depois agir, depois os detalhes.** O plano de ação ("O que fazer agora") é onde o usuário age.
- **Todo dado tem origem visível:** requisição no HAR, identificação, aviso, cálculo.
- **Termo técnico vem explicado** (glossário).
- **Limpo, sem encher linguiça:** só número que ajuda a decidir; cada gráfico traz a conclusão escrita embaixo.
- **Dado simulado é sempre identificado como simulado.**
- **Layout completo por padrão; modo foco opcional** para ler uma zona por vez (Rastreado, Agir, Detalhes).
